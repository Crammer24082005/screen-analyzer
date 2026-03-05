from capture_engine.screen_capture import ScreenCaptureEngine
from capture_engine.capture_config import CaptureConfig
from capture_engine.monitor_manager import MonitorManager
from ai_pipeline.ocr_engine import OCREngine

import cv2
import numpy as np


def main():

    config = CaptureConfig()

    # Prevent preview recursion
    config.REGION = {
        "top": 0,
        "left": 0,
        "width": 1400,
        "height": 800
    }

    monitor_manager = MonitorManager()

    print("Available monitors:")
    for monitor in monitor_manager.monitors:
        print(f"{monitor.index}: {monitor.name} - {monitor.width}x{monitor.height}")

    config.MONITOR_INDEX = 1
    config.FPS = monitor_manager.get_recommended_fps(1)

    engine = ScreenCaptureEngine(config)
    ocr = OCREngine()

    engine.start()

    print("Capture started")
    print("Press ESC or Q to exit")

    texts = []

    try:
        while True:

            packet = engine.get_frame()

            if packet and "frame" in packet:

                frame = packet["frame"]

                # ===== OCR RUNS EVERY FRAME =====
                texts = ocr.extract_text(frame)
                ocr.save_text(texts)

                # ===== SYSTEM METRICS =====
                metrics = engine.get_system_metrics()

                cpu = metrics["cpu_usage"]
                mem = metrics["memory_usage"]
                buffer_size = metrics.get("current_size", 0)
                fps = engine.current_fps

                # Draw metrics background
                cv2.rectangle(frame, (10,10), (260,140), (0,0,0), -1)

                cv2.putText(frame, f"FPS: {fps}", (20,40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"CPU: {cpu:.1f}%", (20,70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"MEM: {mem:.1f}%", (20,100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"Buffer: {buffer_size}", (20,130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                # ===== OCR PANEL =====
                h, w, _ = frame.shape
                panel_height = 200
                panel = np.zeros((panel_height, w, 3), dtype=np.uint8)

                cv2.putText(panel, "OCR OUTPUT", (20,40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                y = 90

                for text in texts:

                    if y > panel_height - 20:
                        break

                    cv2.putText(panel, text, (20, y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0,255,255), 2)

                    y += 40

                # Combine frame + OCR panel
                combined = np.vstack((frame, panel))

                cv2.imshow("AI Screen Analyzer", combined)

                cv2.moveWindow("AI Screen Analyzer", 1200, 50)

            key = cv2.waitKey(1) & 0xFF

            if key == 27 or key == ord('q'):
                print("Exit key pressed")
                break

    finally:

        print("Stopping capture engine...")
        engine.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()