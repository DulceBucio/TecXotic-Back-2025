# test_client.py
import requests

BASE_URL = 'http://192.168.5.1:8080/actuators'  # Change port if different

def send_action(action):
    payload = {"actions": action}
    try:
        response = requests.post(BASE_URL, json=payload)
        print("Sent:", action)
        print("Response:", response.status_code, response.json())
    except Exception as e:
        print("Request failed:", e)

if __name__ == '__main__':
    while True:
        user_input = input("Enter action (e.g., STOP, 1, 2, 90): ").strip().upper()
        if user_input == "EXIT":
            break
        send_action(user_input)
