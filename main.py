# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 13:51:43 2020

@author: Max
"""

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import camera_try
import ctypes
import ctypes.util
import numpy as np
import time

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'ORCAFlashCapture'
        self.left = 100
        self.top = 100
        self.width = 1920
        self.height = 1080
        self.initCamera()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.table_widget = TableWidget(self)
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

class TableWidget(QWidget):
    
    def __init__(self, parent):
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
        
        # Create first tab
        self.captureTab.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("Start Acquire")
        self.captureTab.layout.addWidget(self.pushButton1)
        self.captureTab.setLayout(self.captureTab.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())