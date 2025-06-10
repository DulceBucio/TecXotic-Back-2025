from flask import Response, Blueprint, request, jsonify
import os
from flask_cors import CORS

floatData = Blueprint('floatData', __name__)
CORS(floatData)

FILE_PATH = "received_data.txt"

commands_queue = []

@floatData.route('/send_command', methods=['POST'])
def send_command():
    command = request.json.get('command')
    if command:
        commands_queue.append(command)
        return f"Command '{command}' queued", 200
    return "No command provided", 400

@floatData.route('/get_command', methods=['GET'])
def get_command():
    if commands_queue:
        command = commands_queue.pop(0) 
        return jsonify({"command": command}), 200
    return jsonify({"command": None}), 200
            

@floatData.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        data = request.data.decode('utf-8')
        print(f"[DATA RECEIVED]\n{data}\n")

        with open(FILE_PATH, "a") as f:
            f.write(data + "\n---\n") 

        return "Data received from float", 200

    elif request.method == 'GET':
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r") as f:
                file_content = f.read()
            return file_content, 200
        else: 
            return "No data received yet", 200
            

