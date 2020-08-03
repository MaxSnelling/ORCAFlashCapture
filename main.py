# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 13:51:43 2020

@author: Max
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ORCAFlashCapture'
        self.left = 100
        self.top = 100
        self.width = 1920
        self.height = 1080
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())