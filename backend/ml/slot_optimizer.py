
import datetime
import json
import os

# Load the trained model if present; otherwise use a sane default profile
DEFAULT_SCORES = {str(h): 0.5 for h in range(24)}
DEFAULT_SCORES.update({"9": 0.8, "10": 0.9, "11": 0.9, "14": 0.85, "15": 0.8})

hourly_scores = DEFAULT_SCORES
model_path = os.path.join(os.getcwd(), 'slot_optimizer_model.json')
if os.path.exists(model_path):
    try:
        with open(model_path, 'r') as f:
            hourly_scores = json.load(f)
    except Exception:
        hourly_scores = DEFAULT_SCORES

def predict_slot_score(slot_start: datetime.datetime, slot_end: datetime.datetime) -> float:
    """
    Predicts the optimality of a time slot using a trained model.
    """
    hour = slot_start.hour
    return float(hourly_scores.get(str(hour), 0.1))
