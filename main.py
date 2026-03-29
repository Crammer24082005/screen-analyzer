from capture_engine.screen_capture import ScreenCaptureEngine
from capture_engine.capture_config import CaptureConfig
from capture_engine.monitor_manager import MonitorManager

from ai_pipeline.ocr_engine import OCREngine
from ai_pipeline.genai_engine import GenAIEngine

import cv2
import numpy as np
import time


def main():

    config = CaptureConfig()

    # Prevent recursive capture of preview window
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

    # OCR + Phi3 GenAI
    ocr = OCREngine()
    genai = GenAIEngine(model="phi3")   # 🔥 IMPORTANT CHANGE

    engine.start()

    print("🚀 AI Screen Analyzer Running (Phi-3)")
    print("Press ESC or Q to exit")

    OCR_INTERVAL = 2
    last_ocr_time = 0

    latest_text = ""
    latest_ai_output = ""

    try:
        while True:

            packet = engine.get_frame()

            if packet and "frame" in packet:

                frame = packet["frame"]

                # =========================
                # OCR + GENAI PIPELINE
                # =========================
                if time.time() - last_ocr_time > OCR_INTERVAL:

                    text_context = ocr.extract_text(frame)

                    if text_context:

                        latest_text = text_context
                        ocr.save_text(text_context)

                        # Better prompt for smaller model (Phi-3)
                        refined_text = f"""
                        Describe briefly what is happening on screen:

                        {text_context}

                        Answer in one short sentence.
                        """

                        ai_output = genai.analyze(refined_text)

                        if ai_output:
                            latest_ai_output = ai_output

                    last_ocr_time = time.time()

                # =========================
                # SYSTEM METRICS
                # =========================
                metrics = engine.get_system_metrics()

                cpu = metrics["cpu_usage"]
                mem = metrics["memory_usage"]
                buffer_size = metrics.get("current_size", 0)
                fps = engine.current_fps

                cv2.rectangle(frame, (10,10), (270,140), (0,0,0), -1)

                cv2.putText(frame, f"FPS: {fps}", (20,40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"CPU: {cpu:.1f}%", (20,70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"MEM: {mem:.1f}%", (20,100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                cv2.putText(frame, f"Buffer: {buffer_size}", (20,130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                # =========================
                # OUTPUT PANEL
                # =========================
                h, w, _ = frame.shape
                panel_height = 260
                panel = np.zeros((panel_height, w, 3), dtype=np.uint8)

                # OCR
                cv2.putText(panel, "OCR CONTEXT:", (20,40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

                cv2.putText(panel, latest_text[:90], (20,80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                # GenAI
                cv2.putText(panel, "PHI-3 INSIGHT:", (20,150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                cv2.putText(panel, latest_ai_output[:110], (20,190),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,255,200), 2)

                combined = np.vstack((frame, panel))

                cv2.imshow("AI Screen Analyzer (Phi-3)", combined)
                cv2.moveWindow("AI Screen Analyzer (Phi-3)", 1200, 50)

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