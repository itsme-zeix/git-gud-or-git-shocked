import cv2
from GazeTracking.gaze_tracking import GazeTracking
from command_queue import command_queue

class CustomGazeTracker:
    def __init__(self):
        self.gaze = GazeTracking()
        self.webcam = cv2.VideoCapture(0)
        if not self.webcam.isOpened():
            print("Unable to access the webcam.")
        else:
            print("Webcam accessed successfully.")
        self.running = True

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
        else:
            text = "Not Looking"
            self.send_shock_signal()

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
    
    def send_shock_signal(self):
        print("CustomGazeTracker added '1' to the command queue.")
        command_queue.put('1')
        

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

