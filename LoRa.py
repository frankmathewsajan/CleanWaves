import time
import json
import serial
import serial.tools.list_ports
import requests


def wait_for_usb():
    """
    Waits for a new USB device (serial port) to be attached.
    Returns the device name of the new serial port.
    """
    print("Scanning for available serial ports...")
    initial_ports = {port.device for port in serial.tools.list_ports.comports()}
    print("Initial ports:", initial_ports)
    print("Waiting for a new USB device to be attached...")

    while True:
        current_ports = {port.device for port in serial.tools.list_ports.comports()}
        new_ports = current_ports - initial_ports
        print(new_ports, current_ports)
        if new_ports:
            serial_port = new_ports.pop()
            print(f"New USB device detected: {serial_port}")
            return serial_port
        time.sleep(1)


def main():
    # Wait until a new USB device (ESP8266) is attached
    SERIAL_PORT = wait_for_usb()
    BAUD_RATE = 115200

    try:
        # Initialize the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")

        while True:
            # Read a line from the serial port
            try:
                line = ser.readline().decode('utf-8').strip()
            except Exception as e:
                print(f"Error reading from serial port: {e}")
                continue

            if line:
                try:
                    # Parse the JSON data from the serial line
                    data = json.loads(line)
                    # Verify expected data structure
                    expected_keys = ['temp', 'lat', 'lon', 'alt', 'heading']
                    if all(key in data for key in expected_keys):
                        print("Received valid data:", data)
                        # Send the JSON data as a POST request
                        try:
                            response = requests.post(
                                "http://localhost:8000/api/data/",
                                json=data,
                                headers={'Content-Type': 'application/json'}
                            )
                            response.raise_for_status()
                            print("Data successfully sent to the API. Response:", response.text)
                        except requests.RequestException as http_err:
                            print(f"HTTP error occurred: {http_err}")
                    else:
                        print("Received data missing required fields:", data)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {line}")
    except serial.SerialException as ser_err:
        print(f"Serial error: {ser_err}")
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")


if __name__ == "__main__":
    main()
