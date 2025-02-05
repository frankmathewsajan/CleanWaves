import json
import os
import time

import django
import serial

from bot.models import SensorData

# Setup Django environment (Modify path accordingly)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CleanWaves.settings")
django.setup()


SERIAL_PORT = "COM5"
BAUD_RATE = 115200


def save_to_database(data):
    """Save data to Django database."""
    try:
        SensorData.objects.create(value=data)
        print(f"Data saved: {data}")
    except Exception as e:
        print(f"Error saving to database: {e}")


def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT}...")

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    data = json.loads(line)
                    print("Received:", data)
                    save_to_database(data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {line}")

            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"Serial port {SERIAL_PORT} closed.")


if __name__ == "__main__":
    main()
