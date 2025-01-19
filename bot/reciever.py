import serial
import json
import time
import os

# Configure the serial port (adjust 'COM3' or '/dev/ttyUSB0' to your Arduino port)
SERIAL_PORT = "COM5"  # Replace with your port, e.g., "/dev/ttyUSB0" for Linux
BAUD_RATE = 115200  # Match the baud rate used in the Arduino code
OUTPUT_FILE = "data.json"


def save_data_to_json(data):
    """Appends data to a JSON file."""
    try:
        # Load existing data if the file exists
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # Append the new data
        existing_data.append(data)

        # Save the updated data back to the file
        with open(OUTPUT_FILE, "w") as file:
            json.dump(existing_data, file, indent=4)
        print(f"Data saved: {data}")

    except Exception as e:
        print(f"Error saving data: {e}")


def main():
    # Initialize serial connection
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT}...")

        while True:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()

            if line:
                try:
                    # Parse the line as JSON
                    data = json.loads(line)
                    print("Received:", data)

                    # Save the data to the JSON file
                    save_data_to_json(data)

                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {line}")

            # Sleep to avoid overloading the CPU (optional, adjust if necessary)
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
