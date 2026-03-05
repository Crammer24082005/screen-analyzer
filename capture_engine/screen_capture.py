# screen_capture.py - Fixed version
import mss
import numpy as np
import cv2
import threading
import time
import psutil
from .frame_buffer import FrameBuffer
from .capture_config import CaptureConfig

class ScreenCaptureEngine:
    def __init__(self, config=None):
        self.config = config or CaptureConfig()
        # Don't create MSS here - create it in the thread instead
        self.buffer = FrameBuffer(self.config.BUFFER_SIZE)
        self.running = False
        self.thread = None
        self.frame_interval = 1 / self.config.FPS
        self.frame_count = 0

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
        # Create MSS INSIDE the thread - this fixes the threading issue
        with mss.mss() as sct:
            monitor = sct.monitors[self.config.MONITOR_INDEX]
            
            # Apply region if specified
            if self.config.REGION:
                monitor = {
                    "top": self.config.REGION["top"],
                    "left": self.config.REGION["left"],
                    "width": self.config.REGION["width"],
                    "height": self.config.REGION["height"],
                    "mon": self.config.MONITOR_INDEX
                }
            
            while self.running:
                try:
                    start_time = time.time()
                    
                    # Capture screen
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Create frame packet
                    frame_packet = {
                        "frame": frame,
                        "timestamp": time.time(),
                        "frame_number": self.frame_count,
                        "monitor_id": self.config.MONITOR_INDEX
                    }
                    
                    # Push to buffer (non-blocking)
                    if not self.buffer.push(frame_packet, timeout=0.1):
                        # Buffer full, skip frame
                        pass
                    else:
                        self.frame_count += 1
                    
                    # Maintain FPS
                    elapsed = time.time() - start_time
                    sleep_time = max(0, self.frame_interval - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
                except Exception as e:
                    print(f"Capture error: {e}")
                    time.sleep(0.1)  # Prevent spinning on error

    def get_frame(self):
        return self.buffer.pop()


class OptimizedScreenCaptureEngine(ScreenCaptureEngine):
    def __init__(self, config=None):
        super().__init__(config)
        self.fps_history = []
        
    def get_current_fps(self):
        # Calculate actual FPS from frame count
        if hasattr(self, 'frame_count') and self.frame_count > 0:
            return self.config.FPS  # Simplified for now
        return 0