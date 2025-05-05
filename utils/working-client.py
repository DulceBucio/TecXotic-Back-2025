import requests
import time
import pygame 
from pygame.locals import *

last_command_time = time.time()

def send(position):
    print()
    url = 'http://192.168.5.1:8080/actuators'
    try:
        data = {"angle": position} 
        response = requests.post(url, json=data)
        print("Data sent to actuators. Status code:", response.status_code)
        if response.status_code != 200:
            print("Error from server:", response.text)
    except requests.exceptions.RequestException as e:
        print("Failed to send data to actuators:", e)

def main():
    angleInput = input("introduzca un angulo")
    send(angleInput)
    print('data sent')

main()