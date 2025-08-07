
import csv
import random
import datetime

# Generate a dataset of 1000 reminder interaction events
with open('reminder_interaction_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['user_id', 'task_id', 'reminder_time', 'action']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(1000):
        # Simulate user interacting with reminders at different times
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        reminder_time = datetime.datetime(2025, 1, 1, hour, minute)

        # Simulate different user actions
        action = random.choice(['completed', 'snoozed', 'ignored'])

        writer.writerow({
            'user_id': f'user_{random.randint(1, 10)}',
            'task_id': f'task_{i}',
            'reminder_time': reminder_time.isoformat(),
            'action': action
        })
