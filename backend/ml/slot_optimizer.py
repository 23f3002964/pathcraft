
import datetime
import json

# Load the trained model
with open('slot_optimizer_model.json', 'r') as f:
    hourly_scores = json.load(f)

def predict_slot_score(slot_start: datetime.datetime, slot_end: datetime.datetime) -> float:
    """
    Predicts the optimality of a time slot using a trained model.
    """
    # Get the hour of the day for the slot
    hour = slot_start.hour

    # Return the score for that hour from the trained model
    return hourly_scores.get(str(hour), 0.1) # Default to a low score if the hour is not in the model
