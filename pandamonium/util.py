from threading import Lock


# TODO: Actually respect range limits, and reuse released IDs.
class IDGenerator:
    def __init__(self, id_range):
        self.counter = id_range[0] - 1
        self.lock = Lock()

    def get_new(self):
        with self.lock:
            self.counter += 1
            return self.counter
