import socket
import threading
import sys
import select
import os

from command_queue import command_queue
from custom_gaze_tracker import CustomGazeTracker

from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("MIDDLEWARE_HOST", "127.0.0.1")
PORT = int(os.getenv("MIDDLEWARE_PORT", 1337))


class ArduinoCommunication(threading.Thread):
    def __init__(self):
        super().__init__()
        self.host = HOST 
        self.port = PORT
        self.running = True


    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.host, self.port))
                print(f"Connected to ArduinoMiddleware at {self.host}:{self.port}")

                while self.running:
                    # Check if there's a command from the GazeTracker
                    if len(command_queue) > 0:
                        command = command_queue.popleft()
                        print(f"Sending command to Arduino: {command}")
                        client.sendall(command.encode())

                        # Receive response from Arduino
                        response = client.recv(1024).decode()
                        print(f"Response from Arduino: {response}")

        except Exception as e:
            print(f"Error in ArduinoCommunication thread: {e}")

    def stop(self):
        self.running = False

def main():
    try:
        # Start Arduino communication in a separate thread
        arduino_thread = ArduinoCommunication()
        arduino_thread.start()

        # Run GazeTracker in the main thread
        gaze_tracker = CustomGazeTracker()
        gaze_tracker.start_listening(HOST, PORT)
        # gaze_tracker.run()

        # Cleanup Arduino thread
        arduino_thread.stop()
        arduino_thread.join()

    except Exception as e:
        print(f"Error in main thread: {e}")


if __name__ == "__main__":
    main()

