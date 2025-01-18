import cv2
import mss
import numpy as np
import ocr_reader
import time

class RegionCapture:
    def __init__(self):
        self.HEALTH_BAR_HORIZONTAL_COORDS_PERCENTAGE = 0.3 #percentage of width at which the health will appear
        self.HEALTH_BAR_VERTICAL_COORDS_PERCENTAGE = 0.85
        self.HEALTH_BAR_WIDTH_PERCENTAGE = 0.1
        self.image_count = 0

    def detect_screen_changes(self):
        """
        Captures frames continuously
        """
        last_health_value = None # format of health
        while True:
            with mss.mss() as sct:
                # Define the screen region (full screen if None)
                monitor = sct.monitors[0]
                region = self._get_bottom_30_percent(monitor_dimensions=monitor)
                # Initialize variables
                print("Monitoring screen for changes... Press 'Ctrl+C' to stop.")
                try:
                    # Capture the current frame
                    current_frame = np.array(sct.grab(region))
                    # Convert BGRA to grayscale for comparison
                    gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGRA2GRAY)
                    current_health_value = ocr_reader.read_image(gray_frame)
                    print(f"captured current health value: {current_health_value}")
                    if current_health_value is not None:
                        is_current_health_value_numeric = str.isnumeric(current_health_value)
                        self._save_frame(gray_frame, current_health_value)
                        # Display the current frame (optional)
                        # cv2.imshow("Current Frame", gray_frame)
                        if is_current_health_value_numeric and last_health_value is not None:
                            if (self._has_health_drop(current_health_value, last_health_value)):
                                self._send_electrical_shock_signal()
                            time.sleep(2)
                        elif is_current_health_value_numeric:
                            print(f'last health value:{last_health_value}')
                            print(f"current: {current_health_value}")
                            last_health_value = current_health_value
                    # Exit on pressing ESC
                    if cv2.waitKey(1) & 0xFF == ord("\\"):
                        break

                except KeyboardInterrupt:
                    print("\nMonitoring stopped by user.")
                    break

                finally:
                    cv2.destroyAllWindows()\

    def _has_health_drop(self, current_value, last_value):
        return last_value - current_value > 0

    def _get_bottom_30_percent(self, monitor_dimensions):
        width = int(self.HEALTH_BAR_WIDTH_PERCENTAGE * monitor_dimensions["width"])
        height = int(monitor_dimensions["height"])
        top = int(self.HEALTH_BAR_VERTICAL_COORDS_PERCENTAGE * height)
        left = int(self.HEALTH_BAR_HORIZONTAL_COORDS_PERCENTAGE * monitor_dimensions["width"])
        return {"top": top, "left": left, "width": width, "height": height - top}

    def _send_electrical_shock_signal(self):
        print('shock comes now')

    def _save_frame(self, frame, current_health_value):
        cv2.imwrite(f"./image_{self.image_count}.jpg", frame)
        with open(f"./{self.image_count}.txt", "w") as f:
            f.write(str(current_health_value))
        self.image_count += 1

if __name__ == "__main__":
    # Define the region (optional)
    # region = {"top": 100, "left": 100, "width": 800, "height": 600}  # Example region
    region_capture_instance = RegionCapture()
    region = None  # Set to None for full screen

    # Call the detection function
    region_capture_instance.detect_screen_changes()