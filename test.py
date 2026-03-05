# test_fixed.py - Simple working version
import mss
import cv2
import numpy as np
import threading
import time
from queue import Queue

class SimpleCapture:
    def __init__(self, monitor=1, fps=5):
        self.monitor_idx = monitor
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.running = False
        self.thread = None
        self.queue = Queue(maxsize=5)
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture)
        self.thread.daemon = True
        self.thread.start()
        print("Capture started")
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Capture stopped")
        
    def _capture(self):
        # Create MSS inside the thread
        with mss.mss() as sct:
            monitor = sct.monitors[self.monitor_idx]
            
            while self.running:
                start = time.time()
                
                # Capture
                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Add to queue (remove oldest if full)
                if self.queue.full():
                    try:
                        self.queue.get_nowait()
                    except:
                        pass
                
                self.queue.put(frame)
                
                # Control FPS
                elapsed = time.time() - start
                sleep = max(0, self.frame_interval - elapsed)
                if sleep > 0:
                    time.sleep(sleep)
    
    def get_frame(self):
        try:
            return self.queue.get_nowait()
        except:
            return None

# Main program
print("Simple Screen Capture Test")
print("Press ESC to exit")

# Create and start capture
capture = SimpleCapture(monitor=1, fps=5)
capture.start()

# Display window
cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Capture", 1024, 768)

frame_count = 0

try:
    while True:
        frame = capture.get_frame()
        
        if frame is not None:
            frame_count += 1
            
            # Add info text
            display = frame.copy()
            cv2.putText(display, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show
            cv2.imshow("Capture", display)
        
        # Check for ESC
        if cv2.waitKey(1) == 27:
            break
            
finally:
    capture.stop()
    cv2.destroyAllWindows()
    
print(f"Captured {frame_count} frames")