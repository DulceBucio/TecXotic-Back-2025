from flask import Response, Blueprint, request, jsonify
import os
from flask_cors import CORS

floatData = Blueprint('floatData', __name__)
CORS(floatData)

FILE_PATH = "received_data.txt"

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
            

