import serial
import time
import threading

def start_motor_controller(controller):
    port = motor_controllers.get(controller)[0]
    print(f"Start command sent to {controller}")
    port.write(f"START".encode()) 

def home(controller):
    port = motor_controllers.get(controller)[0]
    while True:
        data = port.readline().decode().strip()
        if data:
            data = -(int)(data)
            if data > 0:
                print(f'Recieved {data} on {controller}')
                return data 

motor_controllers = {
    "X Axis": [serial.Serial('COM3', baudrate=115200, timeout=1)],
    "Y Axis": [serial.Serial('COM4', baudrate=115200, timeout=1)],
    "Z Axis": [serial.Serial('COM5', baudrate=115200, timeout=1)],
    }

print("Initializing...")
time.sleep(2)

for controller, attributes in motor_controllers.items():
    attributes.append(home(controller))

while True:
    for controller, attributes in motor_controllers.items():
        port = attributes[0]
        max_pos = attributes[1]
        pos = input("Position to run to?\n")
        if pos.isdigit():
            pos = (int)(pos)  
            if pos in range(0,max_pos):
                print(f"Moving to {pos}...")
                port.write(f"{pos}\n".encode())  
            else:
                print("Not within range") 
        else:
            print("Invalid input. Enter an integer.")







