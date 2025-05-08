import websockets
import asyncio
import json
import serial
from core.ConnectionPixhawk import Pixhawk
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

px = Pixhawk(direction='/dev/serial/by-id/usb-ArduPilot_Pixhawk1_2A0025000851323438393232-if00')

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

            # px control
            px.drive_manual(
                commands['roll'], commands['pitch'],
                commands['yaw'], commands['throttle'], 0
            )
            handle_pix_mode(commands['mode'])
            handle_motors_arming(commands["arm_disarm"])

            # sensor data
            imuVal = px.get_msg('AHRS2', timeout=0.5)
            imu = {
                "roll": imuVal['roll'],
                "yaw": imuVal['yaw'],
                "pitch": imuVal['pitch']
            }

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