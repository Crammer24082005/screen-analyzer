import psutil
import time

class SystemHealthMonitor:

    def __init__(self):
        self.start_time = time.time()

    def get_metrics(self, buffer_metrics=None):

        cpu = psutil.cpu_percent(interval=0)
        memory = psutil.virtual_memory().percent

        metrics = {
            "cpu_usage": cpu,
            "memory_usage": memory,
            "uptime": time.time() - self.start_time
        }

        if buffer_metrics:
            metrics.update(buffer_metrics)

        return metrics