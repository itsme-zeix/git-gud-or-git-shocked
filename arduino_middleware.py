import socket
import serial
import serial.tools.list_ports
import threading
import time

def find_arduino_port():
    """Find the Arduino device by scanning available serial ports."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise Exception("No serial ports found! Is the Arduino connected?")
    for port in ports:
        print(f"Device: {port.device}, Description: {port.description}, HWID: {port.hwid}")
        if "usbmodem" in port.device:
            return port.device
    raise Exception("Arduino not found!")

class ArduinoMiddleware:
    def __init__(self, host='127.0.0.1', port=1337, baudrate=9600):
        self.arduino_port = find_arduino_port()
        self.arduino = serial.Serial(port=self.arduino_port, baudrate=baudrate, timeout=1)
        self.host = host
        self.port = port
        self.server = None
        self.client_connection = None
        self.is_running = False

    def start_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(1)
            self.is_running = True
            print(f"Arduino middleware server running at {self.host}:{self.port}")
            
            # Accept client connection in a new thread
            threading.Thread(target=self.accept_client_connection, daemon=True).start()
        except Exception as e:
            print(f"Failed to start the server: {e}")

    def accept_client_connection(self):
        while self.is_running:
            try:
                self.client_connection, client_address = self.server.accept()
                print(f"Client connected from {client_address}")
                threading.Thread(target=self.handle_client, daemon=True).start()
            except Exception as e:
                print(f"Error accepting client connection: {e}")

    def handle_client(self):
        try:
            while self.is_running:
                data = self.client_connection.recv(1024).decode().strip()
                if not data:
                    break  # Client disconnected
                
                print(f"Received command from client: {data}")
                self.send_command_to_arduino(data)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            print("Client disconnected")
            self.client_connection.close()

    def send_command_to_arduino(self, command):
        try:
            self.arduino.write(command.encode())
            response = self.arduino.readline().decode().strip()
            print(f"Response from Arduino: {response}")
            
            # Send response back to the client
            if self.client_connection:
                self.client_connection.sendall(response.encode())
        except Exception as e:
            print(f"Error communicating with Arduino: {e}")

    def stop_server(self):
        self.is_running = False
        if self.client_connection:
            self.client_connection.close()
        if self.server:
            self.server.close()
        print("Arduino middleware server stopped")

# Example usage:
if __name__ == "__main__":
    middleware = ArduinoMiddleware()
    try:
        middleware.start_server()
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        middleware.stop_server()

