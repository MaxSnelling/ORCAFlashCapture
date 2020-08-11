# -*- coding: utf-8 -*-
import threading
import time

class FrameCheckThread(threading.Thread):
    """Base class for image acquisition threads."""

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.running = True

    def run(self):
        while self.running:
            print("check")
            self.app.update_image()
            time.sleep(.500)
        
    def stop(self):
        self.running = False
        