import socket
import threading
from command_queue import command_queue
from custom_gaze_tracker import CustomGazeTracker

HOST_MIDDLEWARE = '127.0.0.1'
PORT_MIDDLEWARE = 1337

def main():
    try:
        # Start the GazeTracker in a separate thread
        gaze_tracker = CustomGazeTracker()
        gaze_tracker.run()

        # Connect to ArduinoMiddleware
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST_MIDDLEWARE, PORT_MIDDLEWARE))
            print(f"Connected to ArduinoMiddleware at {HOST_MIDDLEWARE}:{PORT_MIDDLEWARE}")

            while True:
                # Check if there's a command from the GazeTracker
                if not command_queue.empty():
                    command = command_queue.get()
                    print(f"Sending command to Arduino: {command}")
                    client.sendall(command.encode())

                    # Receive response from Arduino
                    response = client.recv(1024).decode()
                    print(f"Response from Arduino: {response}")

                # Allow user to send manual commands
                manual_command = input("Enter command for Arduino (or 'q' to quit): ")
                if manual_command == 'q':
                    print("Exiting client...")
                    gaze_tracker.stop()
                    break

                client.sendall(manual_command.encode())
                response = client.recv(1024).decode()
                print(f"Response from Arduino: {response}")

        # Cleanup
        gaze_tracker.stop()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

