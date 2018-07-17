from threading import Lock


class IDGenerator:
    def __init__(self, start_id=0):
        self.counter = start_id - 1
        self.lock = Lock()

    def get_new(self):
        with self.lock:
            self.counter += 1
            return self.counter
