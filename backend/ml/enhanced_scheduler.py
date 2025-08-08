import datetime
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle

@dataclass
class UserBehaviorPattern:
    user_id: str
    hour: int
    day_of_week: int
    task_completion_rate: float
    productivity_score: float
    focus_time_minutes: int
    task_count: int

@dataclass
class SchedulingContext:
    user_id: str
    task_duration_minutes: int
    task_priority: int
    task_type: str
    deadline: datetime.datetime
    user_preferences: Dict[str, str]
    existing_events: List[Dict]

class EnhancedScheduler:
    def __init__(self, model_path: str = "enhanced_scheduler_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.user_patterns = {}
        self.load_model()
    
    def load_model(self):
        """Load the trained scheduling model."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.user_patterns = model_data.get('user_patterns', {})
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
    
    def save_model(self):
        """Save the trained scheduling model."""
        if self.model is not None:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'user_patterns': self.user_patterns
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
    
    def extract_features(self, context: SchedulingContext, slot_start: datetime.datetime) -> List[float]:
        """Extract features for a time slot."""
        hour = slot_start.hour
        day_of_week = slot_start.weekday()
        
        # Get user pattern for this hour and day
        pattern_key = f"{context.user_id}_{hour}_{day_of_week}"
        pattern = self.user_patterns.get(pattern_key, UserBehaviorPattern(
            context.user_id, hour, day_of_week, 0.5, 0.5, 0, 0
        ))
        
        # Calculate time until deadline
        time_to_deadline = (context.deadline - slot_start).total_seconds() / 3600  # hours
        
        # Check for conflicts with existing events
        conflict_score = self._calculate_conflict_score(slot_start, context.task_duration_minutes, context.existing_events)
        
        # Extract user preferences
        preferred_start_hour = int(context.user_preferences.get('preferred_start_hour', 9))
        preferred_end_hour = int(context.user_preferences.get('preferred_end_hour', 17))
        preferred_timezone = context.user_preferences.get('timezone', 'UTC')
        
        # Calculate preference alignment
        hour_alignment = 1.0 - abs(hour - preferred_start_hour) / 24.0
        
        features = [
            hour,
            day_of_week,
            pattern.task_completion_rate,
            pattern.productivity_score,
            pattern.focus_time_minutes / 60.0,  # Convert to hours
            pattern.task_count,
            context.task_duration_minutes / 60.0,  # Convert to hours
            context.task_priority,
            time_to_deadline,
            conflict_score,
            hour_alignment,
            int(hour >= preferred_start_hour and hour < preferred_end_hour),  # Within preferred hours
            int(day_of_week < 5),  # Weekday
        ]
        
        return features
    
    def _calculate_conflict_score(self, slot_start: datetime.datetime, duration_minutes: int, existing_events: List[Dict]) -> float:
        """Calculate conflict score with existing events."""
        slot_end = slot_start + datetime.timedelta(minutes=duration_minutes)
        conflict_score = 0.0
        
        for event in existing_events:
            event_start = event.get('start')
            event_end = event.get('end')
            
            if event_start and event_end:
                # Check for overlap
                if (slot_start < event_end and slot_end > event_start):
                    overlap_minutes = min(slot_end, event_end) - max(slot_start, event_start)
                    conflict_score += overlap_minutes.total_seconds() / 3600  # hours
        
        return conflict_score
    
    def predict_slot_score(self, context: SchedulingContext, slot_start: datetime.datetime) -> float:
        """Predict the optimality score for a time slot."""
        if self.model is None:
            # Fallback to rule-based scoring
            return self._rule_based_scoring(context, slot_start)
        
        try:
            features = self.extract_features(context, slot_start)
            features_scaled = self.scaler.transform([features])
            score = self.model.predict(features_scaled)[0]
            return max(0.0, min(1.0, score))  # Clamp between 0 and 1
        except Exception as e:
            print(f"Error predicting slot score: {e}")
            return self._rule_based_scoring(context, slot_start)
    
    def _rule_based_scoring(self, context: SchedulingContext, slot_start: datetime.datetime) -> float:
        """Fallback rule-based scoring when ML model is not available."""
        hour = slot_start.hour
        day_of_week = slot_start.weekday()
        
        # Base score
        score = 0.5
        
        # Time of day preference (9 AM - 5 PM is preferred)
        if 9 <= hour <= 17:
            score += 0.3
        elif 8 <= hour <= 18:
            score += 0.1
        
        # Weekday preference
        if day_of_week < 5:  # Monday to Friday
            score += 0.2
        
        # Priority-based scoring
        if context.task_priority == 0:  # High priority
            score += 0.2
        elif context.task_priority == 1:  # Medium priority
            score += 0.1
        
        # Deadline proximity
        time_to_deadline = (context.deadline - slot_start).total_seconds() / 3600
        if time_to_deadline < 24:  # Within 24 hours
            score += 0.3
        elif time_to_deadline < 72:  # Within 3 days
            score += 0.1
        
        return min(1.0, score)
    
    def find_optimal_slots(self, context: SchedulingContext, search_days: int = 7) -> List[Tuple[datetime.datetime, float]]:
        """Find optimal time slots for a task."""
        optimal_slots = []
        current_time = datetime.datetime.now()
        
        # Search for slots in the next N days
        for day_offset in range(search_days):
            search_date = current_time.date() + datetime.timedelta(days=day_offset)
            
            # Search every 30 minutes during working hours
            for hour in range(6, 22):  # 6 AM to 10 PM
                for minute in [0, 30]:
                    slot_start = datetime.datetime.combine(search_date, datetime.time(hour, minute))
                    
                    # Skip past slots
                    if slot_start <= current_time:
                        continue
                    
                    # Predict score for this slot
                    score = self.predict_slot_score(context, slot_start)
                    
                    if score > 0.3:  # Only consider slots with reasonable scores
                        optimal_slots.append((slot_start, score))
        
        # Sort by score (descending) and return top slots
        optimal_slots.sort(key=lambda x: x[1], reverse=True)
        return optimal_slots[:10]  # Return top 10 slots
    
    def update_user_patterns(self, user_id: str, task_completion_data: List[Dict]):
        """Update user behavior patterns based on task completion data."""
        for data in task_completion_data:
            hour = data.get('hour', 0)
            day_of_week = data.get('day_of_week', 0)
            completion_rate = data.get('completion_rate', 0.5)
            productivity_score = data.get('productivity_score', 0.5)
            focus_time = data.get('focus_time_minutes', 0)
            task_count = data.get('task_count', 0)
            
            pattern_key = f"{user_id}_{hour}_{day_of_week}"
            
            if pattern_key in self.user_patterns:
                # Update existing pattern
                pattern = self.user_patterns[pattern_key]
                pattern.task_completion_rate = (pattern.task_completion_rate + completion_rate) / 2
                pattern.productivity_score = (pattern.productivity_score + productivity_score) / 2
                pattern.focus_time_minutes = (pattern.focus_time_minutes + focus_time) / 2
                pattern.task_count = max(pattern.task_count, task_count)
            else:
                # Create new pattern
                self.user_patterns[pattern_key] = UserBehaviorPattern(
                    user_id, hour, day_of_week, completion_rate, productivity_score, focus_time, task_count
                )
    
    def train_model(self, training_data: List[Tuple[List[float], float]]):
        """Train the scheduling model with new data."""
        if not training_data:
            return
        
        X = [features for features, _ in training_data]
        y = [score for _, score in training_data]
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save the model
        self.save_model()

# Global scheduler instance
enhanced_scheduler = EnhancedScheduler()
