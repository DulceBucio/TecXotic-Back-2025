import requests
import time
import pygame 
from pygame.locals import *

current_angle = 330
max_angle = 350
min_angle = 310

def send(position):
    url = 'http://192.168.5.1:8080/actuators'
    try:
        data = {"angle": position} 
        response = requests.post(url, json=data)
        print(f"Sent angle: {position}, Status code: {response.status_code}")
        if response.status_code != 200:
            print("Error from server:", response.text)
    except requests.exceptions.RequestException as e:
        print("Failed to send data to actuators:", e)

def handle_hat_motion(joystick):
    gvalue_x, value_y = joystick.get_hat(0)
    data = {'button_name': "DPad", 'value_x': value_x, 'value_y': value_y}

    if value_y == -1 and value_x == 0:
        send(350)
    elif value_y == 1 and value_x == 0:
        send(310)

def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No se detectaron controles de videojuegos.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print("Joystick conectado:", joystick.get_name())

    try:
        while True:
            for event in pygame.event.get():
                if event.type == JOYHATMOTION:
                    handle_hat_motion(joystick)
            time.sleep(0.1)  # Prevent CPU overload
    except KeyboardInterrupt:
        pygame.quit()
        print("Programa terminado.")

main()
