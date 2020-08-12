# -*- coding: utf-8 -*-
import threading
import time

class FrameCheckThreadLive(threading.Thread):
    """Frame check thread for live feed"""

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.running = True

    def run(self):
        while self.running:
            self.app.update_image()
            time.sleep(.100)
        
    def stop(self):
        self.running = False

class FrameCheckThreadFixed(threading.Thread):
    """Frame check thread for fixed frame feed"""

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.running = True

    def run(self):
        while self.running:
            success = self.app.update_image()
            if success:
                break
            time.sleep(.100)
        