import mss
import numpy as np
import cv2
import threading
import time
import psutil

from .frame_buffer import FrameBuffer
from .capture_config import CaptureConfig
from .preprocessor import FramePreprocessor
from .change_detector import FrameChangeDetector
from .adaptive_fps import AdaptiveFPSController
from .health_monitor import SystemHealthMonitor
from .capture_logger import CaptureLogger


class ScreenCaptureEngine:

    def __init__(self, config=None):

        self.config = config or CaptureConfig()

        self.buffer = FrameBuffer(self.config.BUFFER_SIZE)

        self.preprocessor = FramePreprocessor()
        self.change_detector = FrameChangeDetector()
        self.fps_controller = AdaptiveFPSController(self.config)
        self.health_monitor = SystemHealthMonitor()

        self.logger = CaptureLogger()

        self.running = False
        self.thread = None

        self.frame_count = 0
        self.current_fps = self.config.FPS

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.daemon = True
        self.thread.start()

        print("Capture started")

    def stop(self):

        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        print("Capture stopped")

    def _capture_loop(self):

        with mss.mss() as sct:

            monitor = sct.monitors[self.config.MONITOR_INDEX]

            while self.running:

                start = time.time()

                try:

                    screenshot = sct.grab(monitor)

                    frame = np.array(screenshot)

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    # Preprocess
                    frame = self.preprocessor.process(frame)

                    # Change detection
                    if not self.change_detector.has_changed(frame):
                        continue

                    cpu_usage = psutil.cpu_percent(interval=0)

                    # Adaptive FPS
                    self.current_fps = self.fps_controller.adjust(
                        cpu_usage,
                        self.current_fps
                    )

                    # Assign priority
                    priority = self._assign_priority(frame)

                    frame_packet = {

                        "frame": frame,
                        "timestamp": time.time(),
                        "frame_number": self.frame_count,
                        "monitor_id": self.config.MONITOR_INDEX,
                        "resolution": frame.shape,
                        "system_load": cpu_usage,
                        "fps": self.current_fps

                    }

                    if not self.buffer.push(frame_packet, priority=priority):

                        self.logger.log_drop()

                    else:

                        self.logger.log_frame(self.frame_count)

                        self.frame_count += 1

                    elapsed = time.time() - start

                    interval = 1.0 / self.current_fps

                    sleep_time = max(0, interval - elapsed)

                    if sleep_time > 0:
                        time.sleep(sleep_time)

                except Exception as e:

                    self.logger.log_error(e)

                    time.sleep(0.1)

    def _assign_priority(self, frame):

        # Placeholder logic
        # Later replace with UI detection / login page detection

        brightness = np.mean(frame)

        if brightness < 40:
            return 0

        if brightness < 120:
            return 1

        return 2

    def get_frame(self):

        return self.buffer.pop()

    def get_system_metrics(self):

        return self.health_monitor.get_metrics(
            self.buffer.get_metrics()
        )