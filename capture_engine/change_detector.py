import cv2
import numpy as np

class FrameChangeDetector:

    def __init__(self, threshold=2.5):
        self.prev_frame = None
        self.threshold = threshold

    def has_changed(self, frame):

        if self.prev_frame is None:
            self.prev_frame = frame
            return True

        diff = cv2.absdiff(self.prev_frame, frame)
        change = np.mean(diff)

        self.prev_frame = frame

        return change > self.threshold