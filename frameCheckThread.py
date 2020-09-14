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
            time.sleep(.500)
        
    def stop(self):
        self.running = False
            
class FrameCheckThreadTrigger(threading.Thread):
    """Frame check thread for trigger feed"""

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.running = True

    def run(self):
        while self.running:
            success = self.app.update_image()
            if success:
                self.app.hcam.stopAcquisition()
                self.app.hcam.startAcquisition()
            time.sleep(.100)
            
    def stop(self):
        self.running = False
        self.app.hcam.stopAcquisition()
        