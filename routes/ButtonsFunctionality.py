import json
from flask import Flask, request, Blueprint, jsonify
from flask_cors import CORS
import serial
import time

# Initialize the Flask blueprint
buttons_functionality = Blueprint('buttons_functionality', __name__)
CORS(buttons_functionality)

# Initialize serial connection
def init_serial_connection(port='/dev/ttyUSB0', baudrate=9600):
    try:
        arduino = serial.Serial(port, baudrate=baudrate, timeout=1)
        time.sleep(2)  # Give time for Arduino's reset and bootloader
        print("Arduino connected")
        return arduino
    except Exception as e:
        print(f"ERROR in serial connection initialization: {e}")
        return None

arduino = init_serial_connection()

def send(message):
    try:
        # Ensure the message is a string and ends with a newline
        message_str = f"{message}\n"
        arduino.write(message_str.encode('utf-8'))
        time.sleep(0.5)  # Give time for Arduino to process the command
    except Exception as e:
        print(f"ERROR during command send: {e}")
        if arduino:
            arduino.close()

@buttons_functionality.route('/actuators', methods=['POST'])
def send_actions():
    if not arduino:
        return jsonify({"message": "Arduino not connected", "status": "error"}), 500

    data = request.get_json()
    action = data.get("actions")

    command_map = {
        "STOP": "0",
        "LEFTROLL": "1",
        "RIGHTROLL": "2", 
        "CLAW_MIDOPEN" : "3",
        "CLAW_OPEN" :"4",
        "CLAW_CLOSE" : "5", 
    }

    command = command_map.get(action)

    if command:
        send(command)
    else:
        try:
            # Attempt to convert the action to an integer
            position = int(action)
            if 0 <= position <= 180:
                send(str(position))
            else:
                raise ValueError("Position out of range")
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid command", "status": "error"}), 400

    return jsonify({"message": "Command sent", "status": "success"})


                                    


                                                                                                     