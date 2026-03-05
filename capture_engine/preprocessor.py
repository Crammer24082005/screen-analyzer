import cv2
import numpy as np

class FramePreprocessor:

    def __init__(self, resize=(960, 540), compression=False, quality=85):
        self.resize = resize
        self.compression = compression
        self.quality = quality

    def process(self, frame):
        # Resize to reduce memory
        if self.resize:
            frame = cv2.resize(frame, self.resize)

        # Noise reduction
        frame = cv2.GaussianBlur(frame, (3,3), 0)

        if self.compression:
            _, frame = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            )

        return frame