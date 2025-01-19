import json
from bot.models import SensorData


def save_sensor_data(data):
    try:
        # Parse the data if it's a JSON string
        if isinstance(data, str):
            data = json.loads(data)
        # Save the data to the database
        sensor_data = SensorData(
            temperature=data['temperature'],
            humidity=data['humidity'],
            counter=data['counter']
        )
        sensor_data.save()
    except Exception as e:
        print(f"Error saving data: {e}")
