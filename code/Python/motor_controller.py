import serial
import time

class OutOfBoundsError(Exception):
    def __init__(self, message="Movement exceeds machine bounds"):
        super().__init__(message)

class MotorController():
    def __init__(self, port, baud_rate):
        self.baud_rate = baud_rate
        self.port = port 
        self.arduino = serial.Serial(port, baud_rate, timeout=1)
        self.max = None
        time.sleep(2)

    def home(self):
        print("Sending home command")
        self.arduino.write(b'HOME\n') 
        print("Command sent")
        while True:
            if self.arduino.in_waiting > 0:
                data = self.arduino.readline().decode('utf-8').strip()
                if data.startswith("MAX:"):
                    max = data[4:]
                    max=[abs(int(num)) for num in max.split(",")]
                    self.max = max
                    print(f"Home command completed {max}")
                    return self.max
                
    def move_to_position(self, x,y,z,vx=1000,vy=1000,vz=1000):
        command = f"POS:{x},{y},{z},{vx},{vy},{vz}\n"
        print(command)
        self.arduino.write(command.encode())
        while True:
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                if response == "DONE":
                    print(f"moved to position {x},{y},{z}")
                    break
                elif response == "ERR:OUT_OF_BOUNDS":
                    raise OutOfBoundsError(f"Movement would exceed machine bounds.")

    def move_step(self, dx,dy,dz, vx=1000,vy=1000,vz=1000):
        command = f"STP:{dx},{dy},{dz},{vx},{vy},{vz}\n"
        self.arduino.write(command.encode())
        print("command sent")
        while True:
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                if response == "DONE":
                    print(f"moved {dx} {dy} {dz} with speed {vx}, {vy}, {vz}")
                    break
                elif response == "ERR:OUT_OF_BOUNDS":
                    raise OutOfBoundsError(f"Movement would exceed machine bounds.")

    def move_claw(self, angle):
        if not (0 <= angle <= 80):
            raise ValueError("Claw angle must be between 0 and 180")
        
        command = f"CLW:{angle}\n"
        self.arduino.write(command.encode())
        print(f"Sent claw command: {command.strip()}")
        
        while True:
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                if response == "CLAW_DONE":
                    print("Claw move complete")
                    break
    
    def ping_position(self):
        command = f"PING\n"
        self.arduino.write(command.encode())
        while True:
            if self.arduino.in_waiting:
                response = self.arduino.readline().decode().strip()
                if response.startswith("POS:"):
                    pos = response[4:]
                    pos = [int(n) for n in pos.split(",")]
                    print(f"Current Position: {pos}")
                    return pos