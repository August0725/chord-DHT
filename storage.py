import threading

class Storage:

    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()