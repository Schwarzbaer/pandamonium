# TODO: Make threadsafe
class IDGenerator:
    def __init__(self, start_id=0):
        self.counter = start_id - 1

    def get_new(self):
        self.counter += 1
        return self.counter
