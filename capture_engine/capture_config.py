from dataclasses import dataclass, field
from typing import Optional, List, Dict
import json
import os

@dataclass
class CaptureConfig:
    FPS: int = 2
    BUFFER_SIZE: int = 10
    MONITOR_INDEX: int = 1
    REGION: Optional[Dict] = None
    MASK_REGIONS: List[Dict] = field(default_factory=list)
    
    # New configuration options
    ADAPTIVE_FPS: bool = True
    MIN_FPS: int = 1
    MAX_FPS: int = 60
    TARGET_CPU_USAGE: float = 50.0  # Target CPU usage percentage
    
    COMPRESSION_QUALITY: int = 85  # JPEG quality for compressed frames
    ENABLE_COMPRESSION: bool = False
    
    AUTO_RESTART: bool = True
    MAX_ERROR_RETRIES: int = 5
    
    TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
    
    @classmethod
    def from_file(cls, config_path: str):
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            return cls()
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        return cls(**data)
    
    def validate(self):
        """Validate configuration parameters"""
        if self.FPS < 1:
            raise ValueError("FPS must be at least 1")
        
        if self.BUFFER_SIZE < 1:
            raise ValueError("BUFFER_SIZE must be at least 1")
        
        if self.MONITOR_INDEX < 1:
            raise ValueError("MONITOR_INDEX must be at least 1")
        
        if self.REGION:
            required_keys = ['top', 'left', 'width', 'height']
            if not all(k in self.REGION for k in required_keys):
                raise ValueError("REGION must contain top, left, width, height")
            
            if any(v < 0 for v in self.REGION.values()):
                raise ValueError("REGION dimensions must be non-negative")
        
        if self.ADAPTIVE_FPS:
            if self.MIN_FPS > self.MAX_FPS:
                raise ValueError("MIN_FPS cannot be greater than MAX_FPS")
            
            if self.TARGET_CPU_USAGE < 0 or self.TARGET_CPU_USAGE > 100:
                raise ValueError("TARGET_CPU_USAGE must be between 0 and 100")
        
        return True
    
    def save(self, config_path: str):
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)