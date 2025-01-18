import cv2
import time
from GazeTracking.gaze_tracking import GazeTracking
from command_queue import command_queue

COOLDOWN = 0.5

class CustomGazeTracker:
    def __init__(self):
        self.gaze = GazeTracking()

        # VideoCapture(0) for Windows
        # VideoCapture(1) for MacOS
        self.webcam = cv2.VideoCapture(1)
        if not self.webcam.isOpened():
            print("Unable to access the webcam.")
        else:
            print("Webcam accessed successfully.")
        self.running = True

        self.last_sent_time = 0  # Track the last time a signal was sent
        self.cooldown = COOLDOWN

    def process_frame(self):
        # Read a frame from the webcam
        ret, frame = self.webcam.read()
        if not ret:
            print("Failed to capture frame from webcam.")
            return None

        # Analyze the frame with GazeTracking
        self.gaze.refresh(frame)

        # Annotate the frame for display
        annotated_frame = self.gaze.annotated_frame()

        # Determine gaze direction
        if self._check_if_looking():
            text = "Looking"
            self.send_signal('0') # stop signal
        else:
            text = "Not Looking"
            self.send_signal('1') # shock signal

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
    
    def _check_if_looking(self):
        return self.gaze.is_right() or self.gaze.is_left() or self.gaze.is_center()
    
    def send_signal(self, signal):
        current_time = time.time()
        if current_time - self.last_sent_time >= self.cooldown:  # Check against cooldown
            print(f"CustomGazeTracker added '{signal}' to the command queue.")
            command_queue.put(signal)
            self.last_sent_time = current_time

    def run(self):
        while self.running:
            frame = self.process_frame()
            if frame is not None:
                cv2.imshow("Gaze Tracker", frame)

            # Check for exit signal (Bound to `esc`)
            if cv2.waitKey(1) == 27:
                self.running = False

        self.cleanup()

    def stop(self):
        self.running = False

    def cleanup(self):
        self.webcam.release()
        cv2.destroyAllWindows()
        print("Gaze Tracker stopped")

