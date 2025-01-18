import socket
import threading
import sys
import select

from command_queue import command_queue
from key_listening import KeyListener
from valo_tracking.region_capture import RegionCapture

HOST_MIDDLEWARE = '127.0.0.1'
PORT_MIDDLEWARE = 1337

class ArduinoCommunication(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.host, self.port))
                print(f"Connected to ArduinoMiddleware at {self.host}:{self.port}")

                while self.running:
                    # Check if there's a command from the GazeTracker
                    if not command_queue.empty():
                        command = command_queue.get()
                        print(f"Sending command to Arduino: {command}")
                        client.sendall(command.encode())

                        # Receive response from Arduino
                        response = client.recv(1024).decode()
                        print(f"Response from Arduino: {response}")

                    # Use select to handle non-blocking input
                    print("Enter command for Arduino (or 'q' to quit):\n", end='', flush=True)
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)  # Timeout of 0.1 seconds
                    if ready:
                        manual_command = sys.stdin.readline().strip()
                        if manual_command == 'q':
                            print("Exiting Arduino communication...")
                            self.running = False
                            break

                        client.sendall(manual_command.encode())
                        response = client.recv(1024).decode()
                        if response is not None:
                          print(f"Response from Arduino: {response}")

        except Exception as e:
            print(f"Error in ArduinoCommunication thread: {e}")

    def stop(self):
        self.running = False

def main():
    try:
        # Start Arduino communication in a separate thread
        arduino_thread = ArduinoCommunication(HOST_MIDDLEWARE, PORT_MIDDLEWARE)
        arduino_thread.start()

        # Run RegionCapture on the main thread
        keyboard_listener = KeyListener("\\")
        region_capture = RegionCapture(keyboard_listener)
        region_capture.detect_screen_changes()
        
        # Cleanup Arduino thread
        arduino_thread.stop()
        arduino_thread.join()

    except Exception as e:
        print(f"Error in main thread: {e}")


if __name__ == "__main__":
    main()

