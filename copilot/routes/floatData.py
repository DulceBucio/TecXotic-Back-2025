from flask import Response, Blueprint, request, jsonify
import os
from flask_cors import CORS
from datetime import datetime
import json

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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[DATA RECEIVED AT {timestamp}]\n{data}\n")

        # Store data with timestamp
        with open(FILE_PATH, "a") as f:
            f.write(f"[{timestamp}]\n{data}\n---\n") 

        return "Data received from float", 200

    elif request.method == 'GET':
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r") as f:
                file_content = f.read()
            return file_content, 200
        else: 
            return "No data received yet", 200

@floatData.route('/data', methods=['GET'])
def get_data():
    """Get logged data with optional formatting and filtering"""
    
    if not os.path.exists(FILE_PATH):
        return jsonify({"error": "No data file found", "data": []}), 404
    
    try:
        with open(FILE_PATH, "r") as f:
            file_content = f.read()
        
        # Get query parameters
        format_type = request.args.get('format', 'raw')
        limit = request.args.get('limit', type=int)
        
        if format_type == 'raw':
            if limit:
                entries = file_content.split('\n---\n')
                entries = entries[-limit:] if limit < len(entries) else entries
                return '\n---\n'.join(entries), 200
            return file_content, 200
            
        elif format_type == 'json':
            entries = file_content.split('\n---\n')
            parsed_data = []
            
            for entry in entries:
                entry = entry.strip()
                if entry:
                    data_dict = {"raw": entry}
                    
                    # Extract timestamp
                    if entry.startswith('[') and ']' in entry:
                        timestamp_end = entry.find(']')
                        timestamp_str = entry[1:timestamp_end]
                        try:
                            data_dict['timestamp'] = timestamp_str
                            data_dict['timestamp_iso'] = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").isoformat()
                        except:
                            data_dict['timestamp'] = None
                            data_dict['timestamp_iso'] = None
                        
                        # Get data after timestamp
                        sensor_data = entry[timestamp_end + 1:].strip()
                    else:
                        sensor_data = entry
                        data_dict['timestamp'] = None
                        data_dict['timestamp_iso'] = None
                    
                    # Parse sensor values
                    lines = sensor_data.split('\n')
                    for line in lines:
                        if 'Pressure:' in line:
                            try:
                                data_dict['pressure'] = float(line.split(':')[1].strip().split()[0])
                                data_dict['pressure_unit'] = 'mbar'
                            except:
                                pass
                        elif 'Temperature:' in line:
                            try:
                                data_dict['temperature'] = float(line.split(':')[1].strip().split()[0])
                                data_dict['temperature_unit'] = '°C'
                            except:
                                pass
                        elif 'Depth:' in line:
                            try:
                                data_dict['depth'] = float(line.split(':')[1].strip().split()[0])
                                data_dict['depth_unit'] = 'm'
                            except:
                                pass
                        elif 'Altitude:' in line:
                            try:
                                data_dict['altitude'] = float(line.split(':')[1].strip().split()[0])
                                data_dict['altitude_unit'] = 'm'
                            except:
                                pass
                    
                    parsed_data.append(data_dict)
            
            # Apply limit if specified
            if limit and limit < len(parsed_data):
                parsed_data = parsed_data[-limit:]
            
            return jsonify({
                "total_entries": len(parsed_data),
                "data": parsed_data
            }), 200
            
        elif format_type == 'latest':
            entries = file_content.split('\n---\n')
            latest_entry = None
            
            for entry in reversed(entries):
                entry = entry.strip()
                if entry:
                    latest_entry = entry
                    break
            
            if latest_entry:
                return latest_entry, 200
            else:
                return "No data available", 404
                
        else:
            return jsonify({"error": "Invalid format parameter. Use 'raw', 'json', or 'latest'"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Error reading data: {str(e)}"}), 500


            

