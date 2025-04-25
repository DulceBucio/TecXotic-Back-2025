# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import requests
import time

RANGE = 1000
NEUTRAL = 0
THROTTLE_RANGE = 500
NEUTRAL_THROTTLE = 500

counter = 0

arduino = 0
throttle = 500
roll = 0
pitch = 0
yaw = 0
arm_disarm = True

mode = 'MANUAL'

safeZone = 0.012
power_limit_ref = 1

# Constants for servo control
SERVO_MIN = 0
SERVO_MAX = 180
SERVO_MID = (SERVO_MAX + SERVO_MIN) // 2
servo_position = SERVO_MID

dpad_active = False

# Rate limiting parameters
MIN_COMMAND_INTERVAL = 0.1  # Minimum interval between command sends in seconds
last_command_time = time.time()

def calculate_potency(joystick, trigger):
    temp_power_limit = power_limit_ref if trigger else 1.0
    return int(joystick * RANGE * temp_power_limit)

def calculate_throttle_potency(joystick, trigger):
    temp_power_limit = power_limit_ref if trigger else 1.0
    return int((-joystick * THROTTLE_RANGE) * temp_power_limit + NEUTRAL_THROTTLE)

# Function to handle joystick axis motion
def handle_axis_motion(event, joystick):
    axis_names = {
        0: "JoyStick izquierdo",
        1: "JoyStick izquierdo",
        2: "JoyStick derecho",
        3: "JoyStick derecho", 
    }
    axis_name = axis_names.get(event.axis, "")
    value_x, value_y = 0, 0
    if axis_name == "JoyStick izquierdo":
        value_x = joystick.get_axis(0)
        value_x = -value_x
        value_y = joystick.get_axis(1)
        value_y = -value_y
    elif axis_name == "JoyStick derecho":
        value_x = joystick.get_axis(2)
        value_x = -value_x
        value_y = joystick.get_axis(3)
        value_y = -value_y

    data = {'button_name': axis_name, 'value_x': value_x, 'value_y': value_y}
    return data

def post(commands):
    global last_command_time
    current_time = time.time()
    if current_time - last_command_time >= MIN_COMMAND_INTERVAL:
        try:
            response = requests.post('http://192.168.5.1:55000', json=commands)
            print("Data sent to API. Status code:", response.status_code)
            last_command_time = current_time
        except requests.exceptions.RequestException as e:
            print("Failed to send data to API:", e)
        print(commands)

def post_servo(position):
    print()
    # url = 'http://192.168.5.1:8080/actuators'
    # try:
    #     data = {"actions": position} if isinstance(position, str) else {"actions": str(position)}
    #     response = requests.post(url, json=data)
    #     print("Data sent to actuators. Status code:", response.status_code)
    #     if response.status_code != 200:
    #         print("Error from server:", response.text)
    # except requests.exceptions.RequestException as e:
    #     print("Failed to send data to actuators:", e)

def handle_button_down(event):
    button_names = ["A", "B", "X", "Y", "LB", "RB"]
    button_name = button_names[event.button] if event.button < len(button_names) else str(event.button)
    data = {'button_name': button_name, 'value': event.button}
    post(data)

def handle_button_up(event):
    button_names = ["A", "B", "X", "Y", "LB", "RB"]
    button_name = button_names[event.button] if event.button < len(button_names) else str(event.button)
    data = {'button_name': button_name, 'value': event.button}
    return data

# Function to handle hat motion events and send roll commands
def handle_hat_motion(joystick):
    value_x, value_y = joystick.get_hat(0)
    data = {'button_name': "DPad", 'value_x': value_x, 'value_y': value_y}

    if value_x == 1:  # Left roll
        post_servo('LEFTROLL')
    elif value_x == -1:  # Right roll
        post_servo('RIGHTROLL')
    elif value_y == -1 and value_x == 0:
        post_servo('CLAW_OPEN')
    elif value_y == 1 and value_x == 0:
        post_servo('CLAW_CLOSE')

def main():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No se detectaron controles de videojuegos.")
        return
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    mode = 'MANUAL'
    trigger = False
    global dpad_active
    try:
        while True:
            commands = {
                'throttle': 500,
                'roll': 0,
                'pitch': 0,
                'yaw': 0,
                'arm_disarm': True,
                'mode': mode,
                'arduino': 0,
            }                   
            for event in pygame.event.get():
                if event.type == JOYAXISMOTION:
                    data = handle_axis_motion(event, joystick)
                    lx = 0
                    ly = 0
                    rx = 0
                    ry = 0
                    if data['button_name'] == "JoyStick izquierdo": 
                        lx = data['value_x']
                        ly = data['value_y']
                    elif data['button_name'] == "JoyStick derecho":
                        rx = data['value_x']
                        ry = data['value_y']
                        commands['arduino'] = 5   

                    commands['pitch'] = calculate_potency(-ly, trigger) if abs(ly) > safeZone else NEUTRAL
                    commands['roll'] = calculate_potency(lx, trigger) if abs(lx) > safeZone else NEUTRAL
                    commands['yaw'] = calculate_potency(rx, trigger) if abs(rx) > safeZone else NEUTRAL
                    if abs(ry) > safeZone:
                        commands['throttle'] = calculate_throttle_potency(ry, trigger)

                elif event.type == JOYBUTTONUP:
                    data = handle_button_up(event)
                    if data['button_name'] == "A":
                        mode = 'MANUAL'
                    elif data['button_name'] == "B":
                        mode = 'ACRO'
                    elif data['button_name'] == "X":
                        mode = 'STABILIZE'
                    elif data['button_name'] == "LB" or data['button_name'] == "RB":
                        trigger = True

                elif event.type == JOYBUTTONDOWN:
                    if event.button == 6:  # 'Select' button
                        print("Select button pressed - Resetting servo position")
                        servo_position = 0
                        post_servo(servo_position)
                    elif event.button == 7:  # 'Start' button
                        print("Start button pressed - Resetting servo position")
                        servo_position = 180
                        post_servo('CLAW_CLOSE')
                    else:
                        print(f"Button {event.button} pressed")
                
                elif event.type == JOYHATMOTION:
                    handle_hat_motion(joystick)
                    dpad_active = True if joystick.get_hat(0) != (0, 0) else False

                post(commands)
            
            if dpad_active:
                handle_hat_motion(joystick)

    except KeyboardInterrupt:
        print("\nSaliendo del programa.")
        pygame.quit()

if __name__ == "__main__":
    if counter == 0:
        commands = {
            'throttle': 500,
            'roll': 0,
            'pitch': 0,
            'yaw': 0,
            'arm_disarm': True,
            'mode': mode,
            'arduino': 0,
            'imu': True
        }   
        print("Iniciando programa.")
        print(commands)
        post(commands)
        post_servo(servo_position)
        counter += 1
    main()