import websockets
import asyncio
import json
import serial
from core.ConnectionPixhawk import Pixhawk
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

px = Pixhawk(direction='/dev/serial/by-id/usb-ArduPilot_Pixhawk1_2A0025000851323438393232-if00')

try:
    arduino = serial.Serial(port='/dev/ttyTHS1', baudrate=9600)
except Exception as e:
    print("ERROR in ButtonsFunctionality.py, serial route not founded: " + str(e))

def send(message):
    arduino.write(bytes(message, 'utf-8'))

def handle_motors_arming(cmd):
    try:
        if cmd != px.get_pix_info()['is_armed']:
            px.arm_disarm()
    except KeyError as e:
        print(f"KeyError in handle_motors_arming(): {e}")
    except Exception as e:
        print(f"Error in handle_motors_arming(): {e}")

def handle_pix_mode(mode):
    if mode != px.get_pix_info()['mode']:
        px.change_mode(mode)

clients = set()

async def echo(websocket, path):
    print("pix found")
    clients.add(websocket)
    try:
        async for message in websocket:
            commands = json.loads(message)
            print(commands)
            arduino_cmd = str(commands.get('arduino', '')).strip()
            if arduino_cmd:
                arduino.write(f"{commands['arduino']}\n".encode('utf-8')) # Append newline
                print("Sent to Arduino:", arduino_cmd)
            else:
                print("No Arduino command found in payload.")

            # px control
            px.drive_manual(
                commands['roll'], commands['pitch'],
                commands['yaw'], commands['throttle'], 0
            )
            handle_pix_mode(commands['mode'])
            handle_motors_arming(commands["arm_disarm"])

            try:
                imuVal = px.get_msg('AHRS2', timeout=0.5)
                imu = {
                    "roll": imuVal['roll'],
                    "yaw": imuVal['yaw'],
                    "pitch": imuVal['pitch']
                }
            except Exception as imu_error:
                print(f"IMU data retrieval error: {imu_error}")
                imu = {"roll": 0, "yaw": 0, "pitch": 0}

            send = {
                "message_received": True,
                "imu": imu,
                "pix_info": px.get_pix_info()
            }

            await websocket.send(json.dumps(send))

    except (ConnectionClosedOK, ConnectionClosedError) as e:
        print("Client disconnected:", e)
    except Exception as e:
        print("ERROR in echo():", e)
    finally:
        clients.remove(websocket)
        px.disarm()

def run():
    start_server = websockets.serve(echo, '0.0.0.0', 55000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    run()