import mss
import psutil
import platform
from dataclasses import dataclass
from typing import List, Dict, Optional
import subprocess

@dataclass
class MonitorInfo:
    index: int
    width: int
    height: int
    top: int
    left: int
    is_primary: bool
    name: str
    dpi_scale: float = 1.0

class MonitorManager:
    def __init__(self):
        self.sct = mss.mss()
        self.monitors = self._enumerate_monitors()
        self._refresh_rate_cache = {}
    
    def _enumerate_monitors(self) -> List[MonitorInfo]:
        """Enumerate all monitors with detailed information"""
        monitors = []
        mss_monitors = self.sct.monitors
        
        for i, mon in enumerate(mss_monitors):
            if i == 0:  # Skip the "all monitors" virtual display
                continue
                
            # Detect if this is the primary monitor
            is_primary = mon.get('left', 0) == 0 and mon.get('top', 0) == 0
            
            # Get monitor name (platform-specific)
            name = self._get_monitor_name(i - 1)
            
            # Get DPI scaling
            dpi_scale = self._get_dpi_scale(i - 1)
            
            monitors.append(MonitorInfo(
                index=i,
                width=mon['width'],
                height=mon['height'],
                top=mon['top'],
                left=mon['left'],
                is_primary=is_primary,
                name=name,
                dpi_scale=dpi_scale
            ))
        
        return monitors
    
    def _get_monitor_name(self, index: int) -> str:
        """Get monitor name (platform-specific)"""
        system = platform.system()
        
        if system == "Windows":
            try:
                import win32api
                import win32con
                devices = win32api.EnumDisplayDevices(None, index)
                return devices.DeviceString
            except:
                return f"Monitor {index + 1}"
        
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ['system_profiler', 'SPDisplaysDataType'],
                    capture_output=True, text=True
                )
                # Parse output for monitor names
                return f"Display {index + 1}"
            except:
                return f"Monitor {index + 1}"
        
        else:  # Linux
            return f"Monitor {index + 1}"
    
    def _get_dpi_scale(self, index: int) -> float:
        """Get DPI scaling factor for monitor"""
        system = platform.system()
        
        if system == "Windows":
            try:
                import ctypes
                # Get DPI for specific monitor
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
                return dpi / 96.0  # 96 DPI is 100% scaling
            except:
                return 1.0
        
        return 1.0
    
    def get_recommended_fps(self, monitor_index: int) -> int:
        """Get recommended FPS based on monitor refresh rate"""
        if monitor_index in self._refresh_rate_cache:
            return self._refresh_rate_cache[monitor_index]
        
        system = platform.system()
        recommended = 30  # Default
        
        if system == "Windows":
            try:
                import win32api
                import win32con
                
                # Get refresh rate for primary monitor
                devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
                if devmode.DisplayFrequency > 0:
                    recommended = min(devmode.DisplayFrequency, 60)  # Cap at 60 for capture
            except:
                pass
        
        self._refresh_rate_cache[monitor_index] = recommended
        return recommended
    
    def get_monitor_by_name(self, name: str) -> Optional[MonitorInfo]:
        """Find monitor by name"""
        for monitor in self.monitors:
            if name.lower() in monitor.name.lower():
                return monitor
        return None
    
    def get_monitor_grid(self) -> Dict:
        """Get monitor grid layout information"""
        if not self.monitors:
            return {}
        
        min_x = min(m.left for m in self.monitors)
        min_y = min(m.top for m in self.monitors)
        max_x = max(m.left + m.width for m in self.monitors)
        max_y = max(m.top + m.height for m in self.monitors)
        
        return {
            'width': max_x - min_x,
            'height': max_y - min_y,
            'offset_x': -min_x,
            'offset_y': -min_y,
            'monitors': [
                {
                    'index': m.index,
                    'x': m.left - min_x,
                    'y': m.top - min_y,
                    'width': m.width,
                    'height': m.height
                }
                for m in self.monitors
            ]
        }
    
    def get_system_load(self) -> float:
        """Get current system load for adaptive FPS"""
        return psutil.cpu_percent(interval=0.1)