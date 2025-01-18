import serial
import time

# Replace 'COM3' with the serial port your Arduino is connected to
arduino = serial.Serial(port='/dev/cu.usbmodem1101', baudrate=9600, timeout=1)

def send_command(command):
    arduino.write(command.encode()) 
    time.sleep(0.1)
    response = arduino.readline().decode().strip()
    print(response)

while True:
    cmd = input("Enter command (1 to turn on, 0 to turn off, q to quit): ")
    if cmd == 'q':
        break
    send_command(cmd)

