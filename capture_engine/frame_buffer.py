from queue import Queue, Full, Empty
import threading
import time
from typing import Optional, Any
from collections import deque
import cv2
import numpy as np

class FrameBuffer:
    def __init__(self, max_size=10, priority_levels=3):
        self.buffers = [Queue(maxsize=max_size) for _ in range(priority_levels)]
        self.metrics = {
            'total_frames': 0,
            'dropped_frames': 0,
            'avg_queue_time': 0
        }
        self.lock = threading.Lock()
        self.last_frame_time = {}
    
    def push(self, frame_packet: dict, priority: int = 1, timeout: float = 0.1) -> bool:
        """
        Push frame to buffer with priority (0=highest, 2=lowest)
        Returns True if successful, False if dropped
        """
        try:
            frame_packet['queue_time'] = time.time()
            frame_packet['priority'] = priority
            
            # Store last frame for each priority level
            with self.lock:
                self.last_frame_time[priority] = time.time()
            
            # Try to put with timeout
            self.buffers[priority].put(frame_packet, timeout=timeout)
            
            with self.lock:
                self.metrics['total_frames'] += 1
            
            return True
            
        except Full:
            with self.lock:
                self.metrics['dropped_frames'] += 1
            return False
    
    def pop(self, timeout: float = None, priority_order: list = None) -> Optional[Any]:
        """
        Pop frame with priority ordering
        priority_order: list of priority levels to check in order
        """
        if priority_order is None:
            priority_order = [0, 1, 2]  # Check high priority first
        
        for priority in priority_order:
            try:
                frame = self.buffers[priority].get(timeout=0.001)  # Quick check
                queue_time = time.time() - frame.get('queue_time', time.time())
                
                # Update metrics
                with self.lock:
                    self.metrics['avg_queue_time'] = (
                        0.9 * self.metrics['avg_queue_time'] + 
                        0.1 * queue_time
                    )
                
                return frame
            except Empty:
                continue
        
        # If no priority frames, try any with timeout
        for buffer in self.buffers:
            try:
                return buffer.get(timeout=timeout)
            except Empty:
                continue
        
        return None
    
    def get_metrics(self):
        """Get buffer performance metrics"""
        with self.lock:
            return {
                **self.metrics,
                'current_size': sum(b.qsize() for b in self.buffers),
                'queue_sizes': [b.qsize() for b in self.buffers]
            }
    
    def clear(self):
        """Clear all buffers"""
        for buffer in self.buffers:
            while not buffer.empty():
                try:
                    buffer.get_nowait()
                except Empty:
                    break