"""
Performance monitoring utilities for the game
Provides tools for measuring and tracking performance metrics
"""
import time
from game_core.gameplay.other_components.debug_tools import debug_manager

class PerformanceMonitor:
    """Monitors performance metrics for the game"""

    # Singleton instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PerformanceMonitor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the performance monitor"""
        self.timers = {}
        self.counters = {}
        self.frame_times = []
        self.max_frame_samples = 60  # Store the last 60 frame times
        self.enabled = False

    def enable(self, enable=True):
        """Enable or disable performance monitoring"""
        self.enabled = enable

    def start_timer(self, name):
        """Start a timer with the given name"""
        if not self.enabled:
            return

        self.timers[name] = time.time()

    def end_timer(self, name):
        """End a timer and return the elapsed time"""
        if not self.enabled or name not in self.timers:
            return 0

        elapsed = time.time() - self.timers[name]
        debug_manager.log(f"Timer '{name}' took {elapsed*1000:.2f} ms", "performance")
        return elapsed

    def increment_counter(self, name, amount=1):
        """Increment a counter by the given amount"""
        if not self.enabled:
            return

        if name not in self.counters:
            self.counters[name] = 0

        self.counters[name] += amount

    def get_counter(self, name):
        """Get the value of a counter"""
        if not self.enabled or name not in self.counters:
            return 0

        return self.counters[name]

    def reset_counter(self, name):
        """Reset a counter to zero"""
        if not self.enabled or name not in self.counters:
            return

        self.counters[name] = 0

    def record_frame_time(self, frame_time):
        """Record the time taken to process a frame"""
        if not self.enabled:
            return

        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_samples:
            self.frame_times.pop(0)

    def get_average_fps(self):
        """Calculate the average FPS based on recorded frame times"""
        if not self.enabled or not self.frame_times:
            return 0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0

    def log_performance_stats(self):
        """Log performance statistics"""
        if not self.enabled:
            return

        avg_fps = self.get_average_fps()
        debug_manager.log(f"Average FPS: {avg_fps:.2f}", "performance")

        for name, value in self.counters.items():
            debug_manager.log(f"Counter '{name}': {value}", "performance")

# Create a global instance for easy access
perf_monitor = PerformanceMonitor()
