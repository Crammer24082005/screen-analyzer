class AdaptiveFPSController:

    def __init__(self, config):
        self.config = config

    def adjust(self, cpu_usage, current_fps):

        if not self.config.ADAPTIVE_FPS:
            return current_fps

        if cpu_usage > self.config.TARGET_CPU_USAGE:
            current_fps = max(self.config.MIN_FPS, current_fps - 1)

        else:
            current_fps = min(self.config.MAX_FPS, current_fps + 1)

        return current_fps