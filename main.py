from capture_engine import OptimizedScreenCaptureEngine, CaptureConfig
from capture_engine.monitor_manager import MonitorManager
import cv2
import time

def main():
    # Load configuration
    config = CaptureConfig.from_file("config.json")
    
    # List available monitors
    monitor_manager = MonitorManager()
    print("Available monitors:")
    for monitor in monitor_manager.monitors:
        print(f"  {monitor.index}: {monitor.name} - {monitor.width}x{monitor.height}")
    
    # Configure for best performance
    config.MONITOR_INDEX = 1
    config.FPS = monitor_manager.get_recommended_fps(1)
    config.ADAPTIVE_FPS = True
    config.TARGET_CPU_USAGE = 60
    
    # Initialize engine
    engine = OptimizedScreenCaptureEngine(config)
    
    # Add callbacks
    def on_frame(frame_packet):
        # Process frame (e.g., for OCR)
        pass
    
    def on_error(error):
        print(f"Capture error: {error}")
    
    engine.on_frame_captured = on_frame
    engine.on_error = on_error
    
    # Start capture
    engine.start()
    
    try:
        # Main loop
        while True:
            # Get frame with priority (0=highest)
            packet = engine.buffer.pop(priority_order=[0, 1, 2])
            
            if packet and 'frame' in packet:
                frame = packet['frame']
                
                # Handle compressed frames
                if engine.config.ENABLE_COMPRESSION and isinstance(frame, bytes):
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                
                # Display
                cv2.imshow("Screen Capture", frame)
                
                # Show performance info
                fps = engine.get_current_fps()
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if cv2.waitKey(1) == 27:  # ESC
                break
    
    finally:
        engine.stop()
        cv2.destroyAllWindows()
    
    # Save updated config
    config.save("config.json")

if __name__ == "__main__":
    main()