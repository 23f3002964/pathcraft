
import csv
import json
import datetime
from collections import defaultdict

# Read the training data
completion_times_by_hour = defaultdict(int)
with open('task_completion_data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        completion_time = datetime.datetime.fromisoformat(row['completion_time'])
        completion_times_by_hour[completion_time.hour] += 1

# Calculate the average completion time for each hour
hourly_scores = {}
for hour, count in completion_times_by_hour.items():
    hourly_scores[hour] = count / 1000 # Normalize the score

# Save the model to a file
with open('slot_optimizer_model.json', 'w') as f:
    json.dump(hourly_scores, f)
