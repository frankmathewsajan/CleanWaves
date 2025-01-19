import os
import django
import serial
import json
import time

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bot.settings")
django.setup()

from bot.utils import save_sensor_data

# Configure the serial port (adjust 'COM10' or '/dev/ttyUSB0' to your Arduino port)
SERIAL_PORT = "COM10"  # Replace with your port, e.g., "/dev/ttyUSB0" for Linux
BAUD_RATE = 115200  # Match the baud rate used in the Arduino code


def main():
    # Initialize serial connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT}...")

        while True:
            try:
                # Read a line from the serial port
                line = ser.readline().decode('utf-8').strip()

                if line:
                    try:
                        # Parse the line as JSON
                        data = json.loads(line)
                        print("Received:", data)

                        # Save the data to the Django database
                        save_sensor_data(data)

                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {line}")

            except serial.SerialException as e:
                print(f"Serial error: {e}")
                break

    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()
