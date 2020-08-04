# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 13:51:43 2020

@author: Max
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
                             QTabWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, Qt
import camera_try
import ctypes
import ctypes.util
import numpy as np
import time
import pyqtgraph as pg

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ORCAFlashCapture'
        self.left = 100
        self.top = 100
        self.width = 1920
        self.height = 1080
        #hcam = self.initCamera()
        hcam = None
        self.initUI(hcam)
        
    def initUI(self, hcam):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = TableWidget(self, hcam)
        self.setCentralWidget(self.table_widget)
        self.show()
    
    def initCamera(self):
        dcam = ctypes.windll.dcamapi
        print(dcam)
        paraminit = camera_try.DCAMAPI_INIT(0, 0, 0, 0, None, None) 
        paraminit.size = ctypes.sizeof(paraminit)
        error_code = dcam.dcamapi_init(ctypes.byref(paraminit))
        if (error_code != camera_try.DCAMERR_NOERROR):
            raise camera_try.DCAMException("DCAM initialization failed with error code " + str(error_code))
        
        n_cameras = paraminit.iDeviceCount    
        print("found: {} cameras".format(n_cameras))
        hcam = camera_try.HamamatsuCameraMR(camera_id = 0)
        print("camera 0 model:", hcam.getModelInfo(0))
        return hcam

class TableWidget(QWidget):
    
    def __init__(self, parent, hcam):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.captureTab = QWidget()
        self.analyseTab = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.captureTab,"Capture")
        self.tabs.addTab(self.analyseTab, "Analyse")
        
        # Capture Tab
        self.horizontalGroupBox = QGroupBox("Grid")
        self.captureTab.layout = QGridLayout(self)
        
        captureText = QLabel("Capture", self)
        captureText.setFont(QFont(captureText.font().family(), 24, QFont.Bold))
        captureText.setAlignment(Qt.AlignCenter)
        self.captureTab.layout.addWidget(captureText, 0,0, 1,3)
        
        startButton = QPushButton("Start Acquire", self)
        startButton.resize(startButton.sizeHint())
        #pushButton1.clicked.connect(hcam.startAcquisition())
        self.captureTab.layout.addWidget(startButton, 1,0, 1,1)
        
        stopButton = QPushButton("Stop Acquire", self)
        stopButton.resize(stopButton.sizeHint())
        #pushButton1.clicked.connect(hcam.stopAcquisition())
        self.captureTab.layout.addWidget(stopButton, 1,1, 1,1)
        
        im_widget = pg.GraphicsLayoutWidget()
        viewbox = im_widget.addViewBox()
        self.im_canvas = pg.ImageItem()
        viewbox.addItem(self.im_canvas)
        self.captureTab.layout.addWidget(im_widget, 2,0, 1,3)
        
        self.captureTab.setLayout(self.captureTab.layout)
        
        #Analyse Tab
        analyseText = QLabel("Capture", self)
        analyseText.setFont(QFont(analyseText.font().family(), 24, QFont.Bold))
        analyseText.setAlignment(Qt.AlignCenter)
        self.analyseTab.layout.addWidget(analyseText, 0,0, 1,3)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())