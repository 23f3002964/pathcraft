import datetime
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle

@dataclass
class ReminderContext:
    user_id: str
    task_id: str
    task_priority: int
    task_deadline: datetime.datetime
    user_response_history: List[Dict]  # Previous reminder responses
    task_completion_rate: float
    user_preferences: Dict[str, str]

@dataclass
class ReminderStrategy:
    frequency_hours: int
    intensity: str  # "gentle", "moderate", "urgent"
    channels: List[str]  # ["push", "email", "sms"]
    escalation_enabled: bool
    custom_message: Optional[str] = None

class EnhancedReminderSystem:
    def __init__(self, model_path: str = "enhanced_reminder_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.user_reminder_patterns = {}
        self.load_model()
    
    def load_model(self):
        """Load the trained reminder model."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.user_reminder_patterns = model_data.get('user_reminder_patterns', {})
            except Exception as e:
                print(f"Error loading reminder model: {e}")
                self.model = None
    
    def save_model(self):
        """Save the trained reminder model."""
        if self.model is not None:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'user_reminder_patterns': self.user_reminder_patterns
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
    
    def extract_features(self, context: ReminderContext) -> List[float]:
        """Extract features for reminder strategy prediction."""
        # Time until deadline
        time_to_deadline = (context.task_deadline - datetime.datetime.now()).total_seconds() / 3600  # hours
        
        # User response patterns
        response_rate = self._calculate_response_rate(context.user_response_history)
        avg_response_time = self._calculate_avg_response_time(context.user_response_history)
        
        # Task urgency based on priority and deadline
        urgency_score = self._calculate_urgency_score(context.task_priority, time_to_deadline)
        
        # User preferences
        preferred_reminder_frequency = int(context.user_preferences.get('preferred_reminder_frequency_hours', 24))
        preferred_channels = context.user_preferences.get('preferred_reminder_channels', 'push').split(',')
        
        # Historical completion rate
        completion_rate = context.task_completion_rate
        
        features = [
            time_to_deadline,
            context.task_priority,
            response_rate,
            avg_response_time,
            urgency_score,
            completion_rate,
            preferred_reminder_frequency,
            len(preferred_channels),
            int('push' in preferred_channels),
            int('email' in preferred_channels),
            int('sms' in preferred_channels),
        ]
        
        return features
    
    def _calculate_response_rate(self, response_history: List[Dict]) -> float:
        """Calculate user response rate to reminders."""
        if not response_history:
            return 0.5  # Default response rate
        
        total_reminders = len(response_history)
        responded_reminders = sum(1 for r in response_history if r.get('responded', False))
        return responded_reminders / total_reminders if total_reminders > 0 else 0.5
    
    def _calculate_avg_response_time(self, response_history: List[Dict]) -> float:
        """Calculate average response time in hours."""
        if not response_history:
            return 24.0  # Default 24 hours
        
        response_times = []
        for r in response_history:
            if r.get('responded', False) and 'sent_time' in r and 'response_time' in r:
                sent_time = r['sent_time']
                response_time = r['response_time']
                if isinstance(sent_time, str):
                    sent_time = datetime.datetime.fromisoformat(sent_time)
                if isinstance(response_time, str):
                    response_time = datetime.datetime.fromisoformat(response_time)
                response_times.append((response_time - sent_time).total_seconds() / 3600)
        
        return np.mean(response_times) if response_times else 24.0
    
    def _calculate_urgency_score(self, priority: int, time_to_deadline: float) -> float:
        """Calculate urgency score based on priority and deadline proximity."""
        # Priority weight (0 = high, 1 = medium, 2 = low)
        priority_weight = 1.0 - (priority / 2.0)
        
        # Deadline proximity weight
        if time_to_deadline < 1:  # Less than 1 hour
            deadline_weight = 1.0
        elif time_to_deadline < 24:  # Less than 1 day
            deadline_weight = 0.8
        elif time_to_deadline < 72:  # Less than 3 days
            deadline_weight = 0.6
        elif time_to_deadline < 168:  # Less than 1 week
            deadline_weight = 0.4
        else:
            deadline_weight = 0.2
        
        return (priority_weight + deadline_weight) / 2.0
    
    def predict_reminder_strategy(self, context: ReminderContext) -> ReminderStrategy:
        """Predict optimal reminder strategy for a task."""
        if self.model is None:
            return self._rule_based_strategy(context)
        
        try:
            features = self.extract_features(context)
            features_scaled = self.scaler.transform([features])
            
            # Predict frequency (hours between reminders)
            frequency_prediction = self.model.predict(features_scaled)[0]
            frequency_hours = max(1, min(168, int(frequency_prediction)))  # Between 1 hour and 1 week
            
            # Determine intensity based on urgency and user patterns
            intensity = self._determine_intensity(context)
            
            # Determine channels based on user preferences and urgency
            channels = self._determine_channels(context, intensity)
            
            # Enable escalation for urgent tasks
            escalation_enabled = context.task_priority == 0 or self._calculate_urgency_score(context.task_priority, 
                (context.task_deadline - datetime.datetime.now()).total_seconds() / 3600) > 0.8
            
            return ReminderStrategy(
                frequency_hours=frequency_hours,
                intensity=intensity,
                channels=channels,
                escalation_enabled=escalation_enabled
            )
        except Exception as e:
            print(f"Error predicting reminder strategy: {e}")
            return self._rule_based_strategy(context)
    
    def _rule_based_strategy(self, context: ReminderContext) -> ReminderStrategy:
        """Fallback rule-based reminder strategy."""
        time_to_deadline = (context.task_deadline - datetime.datetime.now()).total_seconds() / 3600
        
        # Determine frequency based on deadline proximity
        if time_to_deadline < 1:  # Less than 1 hour
            frequency_hours = 0.5  # Every 30 minutes
        elif time_to_deadline < 24:  # Less than 1 day
            frequency_hours = 2
        elif time_to_deadline < 72:  # Less than 3 days
            frequency_hours = 6
        elif time_to_deadline < 168:  # Less than 1 week
            frequency_hours = 12
        else:
            frequency_hours = 24
        
        # Adjust frequency based on priority
        if context.task_priority == 0:  # High priority
            frequency_hours = max(1, frequency_hours // 2)
        elif context.task_priority == 2:  # Low priority
            frequency_hours = frequency_hours * 2
        
        # Determine intensity
        urgency_score = self._calculate_urgency_score(context.task_priority, time_to_deadline)
        if urgency_score > 0.8:
            intensity = "urgent"
        elif urgency_score > 0.5:
            intensity = "moderate"
        else:
            intensity = "gentle"
        
        # Determine channels
        preferred_channels = context.user_preferences.get('preferred_reminder_channels', 'push').split(',')
        if intensity == "urgent":
            channels = ["push", "email"] if "email" in preferred_channels else ["push"]
        elif intensity == "moderate":
            channels = ["push"]
        else:
            channels = preferred_channels[:1]  # Use only the first preferred channel
        
        return ReminderStrategy(
            frequency_hours=frequency_hours,
            intensity=intensity,
            channels=channels,
            escalation_enabled=urgency_score > 0.8
        )
    
    def _determine_intensity(self, context: ReminderContext) -> str:
        """Determine reminder intensity based on context."""
        time_to_deadline = (context.task_deadline - datetime.datetime.now()).total_seconds() / 3600
        urgency_score = self._calculate_urgency_score(context.task_priority, time_to_deadline)
        
        if urgency_score > 0.8 or time_to_deadline < 2:
            return "urgent"
        elif urgency_score > 0.5 or time_to_deadline < 24:
            return "moderate"
        else:
            return "gentle"
    
    def _determine_channels(self, context: ReminderContext, intensity: str) -> List[str]:
        """Determine reminder channels based on intensity and user preferences."""
        preferred_channels = context.user_preferences.get('preferred_reminder_channels', 'push').split(',')
        
        if intensity == "urgent":
            # Use multiple channels for urgent reminders
            channels = []
            if "push" in preferred_channels:
                channels.append("push")
            if "email" in preferred_channels:
                channels.append("email")
            if "sms" in preferred_channels and context.task_priority == 0:
                channels.append("sms")
            return channels if channels else ["push"]
        elif intensity == "moderate":
            # Use primary channel
            return preferred_channels[:1] if preferred_channels else ["push"]
        else:
            # Use least intrusive channel
            return ["push"] if "push" in preferred_channels else preferred_channels[:1]
    
    def generate_reminder_message(self, context: ReminderContext, strategy: ReminderStrategy) -> str:
        """Generate a personalized reminder message."""
        time_to_deadline = (context.task_deadline - datetime.datetime.now()).total_seconds() / 3600
        
        if strategy.intensity == "urgent":
            if time_to_deadline < 1:
                return f"🚨 URGENT: Task due in {int(time_to_deadline * 60)} minutes!"
            else:
                return f"⚠️ High Priority: Task due in {int(time_to_deadline)} hours"
        elif strategy.intensity == "moderate":
            if time_to_deadline < 24:
                return f"📅 Reminder: Task due in {int(time_to_deadline)} hours"
            else:
                return f"📋 Task reminder: Due in {int(time_to_deadline / 24)} days"
        else:
            return f"💡 Gentle reminder: You have a task coming up"
    
    def should_send_reminder(self, task_id: str, last_reminder_time: Optional[datetime.datetime], 
                           strategy: ReminderStrategy) -> bool:
        """Determine if a reminder should be sent based on frequency."""
        if last_reminder_time is None:
            return True
        
        time_since_last = (datetime.datetime.now() - last_reminder_time).total_seconds() / 3600
        return time_since_last >= strategy.frequency_hours
    
    def update_user_patterns(self, user_id: str, reminder_response_data: List[Dict]):
        """Update user reminder response patterns."""
        for data in reminder_response_data:
            response_time = data.get('response_time_hours', 24)
            responded = data.get('responded', False)
            task_priority = data.get('task_priority', 1)
            
            pattern_key = f"{user_id}_{task_priority}"
            
            if pattern_key in self.user_reminder_patterns:
                pattern = self.user_reminder_patterns[pattern_key]
                pattern['avg_response_time'] = (pattern['avg_response_time'] + response_time) / 2
                pattern['response_rate'] = (pattern['response_rate'] + (1 if responded else 0)) / 2
            else:
                self.user_reminder_patterns[pattern_key] = {
                    'avg_response_time': response_time,
                    'response_rate': 1 if responded else 0
                }
    
    def train_model(self, training_data: List[Tuple[List[float], float]]):
        """Train the reminder model with new data."""
        if not training_data:
            return
        
        X = [features for features, _ in training_data]
        y = [frequency for _, frequency in training_data]
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save the model
        self.save_model()

# Global reminder system instance
enhanced_reminder_system = EnhancedReminderSystem()
