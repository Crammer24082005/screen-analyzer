import logging

class CaptureLogger:

    def __init__(self, log_file="capture.log"):

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )

        self.logger = logging.getLogger("capture")

    def log_frame(self, frame_number):
        self.logger.info(f"Frame captured: {frame_number}")

    def log_drop(self):
        self.logger.warning("Frame dropped")

    def log_error(self, error):
        self.logger.error(f"Capture error: {error}")