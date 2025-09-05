import time
import threading

class ProgressTracker:
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.operation_name = operation_name
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update(self, increment: int = 1):
        with self.lock:
            self.current_item += increment
            progress = (self.current_item / self.total_items) * 100 if self.total_items else 100
            elapsed = time.time() - self.start_time
            if self.current_item > 0 and self.total_items:
                eta = (elapsed / self.current_item) * (self.total_items - self.current_item)
                print(f"🔄 {self.operation_name}: {self.current_item}/{self.total_items} ({progress:.1f}%) - ETA: {eta:.1f}s")
            else:
                print(f"🔄 {self.operation_name}: {self.current_item}/{self.total_items} ({progress:.1f}%)")

    def complete(self):
        elapsed = time.time() - self.start_time
        print(f"✅ {self.operation_name} completed in {elapsed:.2f}s")

__all__ = ['ProgressTracker']
