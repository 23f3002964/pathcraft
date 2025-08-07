
import csv
import random
import datetime

# Generate a dataset of 1000 task completion events
with open('task_completion_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['user_id', 'task_id', 'completion_time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(1000):
        # Simulate user completing tasks at different times of the day
        hour = random.randint(8, 22) # Users are most active between 8am and 10pm
        minute = random.randint(0, 59)
        completion_time = datetime.datetime(2025, 1, 1, hour, minute)

        writer.writerow({
            'user_id': f'user_{random.randint(1, 10)}',
            'task_id': f'task_{i}',
            'completion_time': completion_time.isoformat()
        })
