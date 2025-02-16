import cv2
import time
from threading import Thread
from GazeTracking.gaze_tracking import GazeTracking
from command_queue import command_queue
from flask import Flask, request, jsonify
# from waitress import serve

NOT_LOOKING_THRESHOLD = 1.0 # Time that user not looking at the screen to trigger shock

class CustomGazeTracker:
    def __init__(self):
        self.gaze = GazeTracking()
        self.app = Flask(__name__)
        self.app.add_url_rule("/start", 'start', self.run, methods = ["GET"])
        self.app.add_url_rule("/stop", 'stop', self.stop, methods = ["GET"])


        self.running = True
        self.last_sent_signal = None
        self.not_looking_start_time = None


    def process_frame(self):
        # Read a frame from the webcam
        ret, frame = self.webcam.read()
        if not ret:
            print("Failed to capture frame from webcam.")
            return None

        # Analyze the frame with GazeTracking
        self.gaze.refresh(frame)

        # Determine gaze direction
        if self._check_if_looking():
            text = "Looking"
            self.not_looking_start_time = None
            self.send_signal('0') # stop signal
        else:
            text = "Not Looking"
            self._track_not_looking()

        # Annotate the frame for display
        annotated_frame = self.gaze.annotated_frame()

        # Add text annotation to the frame
        cv2.putText(
            annotated_frame,
            text,
            (60, 60),
            cv2.FONT_HERSHEY_COMPLEX_SMALL,
            2,
            (255, 0, 0),
            2,
        )

        return annotated_frame
    
    def _track_not_looking(self):
        current_time = time.time()

        if self.not_looking_start_time is None:
            self.not_looking_start_time = current_time

        elapsed_time = current_time - self.not_looking_start_time

        if elapsed_time >= NOT_LOOKING_THRESHOLD:
            self.send_signal('1')

    def _check_if_looking(self):
        return self.gaze.is_right() or self.gaze.is_left() or self.gaze.is_center()
    
    def send_signal(self, signal):
        if self.last_sent_signal == signal:
            return  # Skip if the last signal is the same

        command_queue.append(signal)
        self.last_sent_signal = signal

    def run(self):
        self.running = True
        self.webcam = cv2.VideoCapture(1)
        if not self.webcam.isOpened():
            print("Unable to access the webcam.")
            return jsonify({"message": "Failed to access the webcam."}), 500

        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        print("Gaze Tracker started.")
        try:
            while self.running:
                frame = self.process_frame()
                # Uncomment for visualization
                # if frame is not None:
                #     cv2.imshow("Gaze Tracker", frame)

                # Add a small sleep to avoid high CPU usage
                time.sleep(0.03)

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"message": f"Error occurred: {e}"}), 500

        finally:
            self.cleanup()

        return jsonify({"message": "Successfully terminated service."})

    def stop(self):
        if not self.running:
            return jsonify({"message": "Service is not running."}), 400
        
        # Force turn off LED so user isn't stuck getting shocked.
        self.send_signal(False) 

        self.running = False
        self.cleanup()
        return jsonify({"message": "Stopped service."})

    def cleanup(self):
        self.webcam.release()
        cv2.destroyAllWindows()
        print("Gaze Tracker stopped")

    def start_listening(self, host, port):
        print(f"API listening on {host}:{port}. Awaiting GET /start or GET /stop.")
        thread = Thread(target=self.app.run, kwargs={"host": host, "port": port, "use_reloader": False})
        thread.daemon = True
        thread.start()

