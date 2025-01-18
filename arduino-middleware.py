import serial
import time
import socket

# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('127.0.0.1', 1337)) 
# server_socket.listen(1)
# print("Waiting for connection...")
#
# conn, addr = server_socket.accept()
# print(f"Connection from {addr}")
#
# Replace 'COM3' with the serial port your Arduino is connected to
arduino = serial.Serial(port='/dev/cu.usbmodem1101', baudrate=9600, timeout=1)

def send_command(command):
    arduino.write(command.encode()) 
    time.sleep(0.1)
    response = arduino.readline().decode().strip()
    print(response)

while True:
    cmd = input("Enter command (1 to turn on, 0 to turn off, q to quit): ")
    # cmd = conn.recv(1024).decode(
    if cmd == 'q':
        break
    if cmd == '1':
      send_command(cmd)
      time.sleep(1)
      cmd = '0'
      send_command(cmd)
    elif cmd == '0':
      send_command(cmd)
      
