import json
from flask import Flask, request, Blueprint
import serial
buttons_functionality = Blueprint('buttons_functionality', __name__)
try:
    arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=5)
except Exception as e:
    print("ERROR in ButtonsFunctionality.py, serial route not founded: " + str(e))


def send(message):
    try:
        arduino.write(bytes(message, 'utf-8'))
    except Exception as e:
        print("ERROR in ButtonsFunctionality.py, arduino.write failed: " + str(e))
        arduino.close()

@buttons_functionality.route('/actuators', methods=['POST'])
def send_actions():
    json = request.get_json()
    print('json_respone: ', str(json["actions"]))
    send(str(json["actions"]))
    return ""