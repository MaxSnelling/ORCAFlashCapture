#!/usr/bin/env python
"""
Script based on the code from the Zhuang Lab, Harvard University (license below),
originally used for controlling the Orca Flash 4.0 V2 of the Hamamatsu.

I rewrote some parts of the code for adapting it from
version V2 to version V3. 

Just used for testing the Orca Flash 4.0 V3 camera (don't take it seriously).

Michele Castriotta (@mikics on github), Politecnico di Milano 
Andrea Bassi, Politecnico di Milano

11/18
"""
"""
A ctypes based interface to Hamamatsu camera.
(tested on a sCMOS Flash 4.0).

The documentation is a little confusing to me on this subject..
I used c_int32 when this is explicitly specified, otherwise I use c_int.

Hazen 10/13

George 11/17 - Updated for SDK4 and to allow fixed length acquisition
"""

import ctypes
import ctypes.util
import numpy as np
import time

import storm_control.sc_library.halExceptions as halExceptions


# Hamamatsu constants.

# DCAM4 API.
DCAMERR_ERROR = 0
DCAMERR_NOERROR = 1

DCAMPROP_ATTR_HASRANGE = int("0x80000000", 0)
DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)
DCAMPROP_ATTR_READABLE = int("0x00010000", 0)
DCAMPROP_ATTR_WRITABLE = int("0x00020000", 0)

DCAMPROP_OPTION_NEAREST = int("0x80000000", 0)
DCAMPROP_OPTION_NEXT = int("0x01000000", 0)     
DCAMPROP_OPTION_SUPPORT = int("0x00000000", 0)

DCAMPROP_TYPE_MODE = int("0x00000001", 0)
DCAMPROP_TYPE_LONG = int("0x00000002", 0)
DCAMPROP_TYPE_REAL = int("0x00000003", 0)
DCAMPROP_TYPE_MASK = int("0x0000000F", 0)

DCAMPROP_TRIGGERSOURCE__INTERNAL = 1
DCAMPROP_TRIGGERSOURCE__EXTERNAL = 2

DCAMPROP_TRIGGER_MODE__NORMAL = 1
DCAMPROP_TRIGGER_MODE__START = 6

DCAMPROP_TRIGGERPOLARITY__NEGATIVE = 1
DCAMPROP_TRIGGERPOLARITY__POSITIVE = 2

DCAMPROP_TRIGGERACTIVE__EDGE = 1
DCAMPROP_TRIGGERACTIVE__LEVEL = 2
DCAMPROP_TRIGGERACTIVE__SYNCREADOUT = 3

DCAMCAP_STATUS_ERROR = int("0x00000000", 0)
DCAMCAP_STATUS_BUSY = int("0x00000001", 0)
DCAMCAP_STATUS_READY = int("0x00000002", 0)
DCAMCAP_STATUS_STABLE = int("0x00000003", 0)
DCAMCAP_STATUS_UNSTABLE = int("0x00000004", 0)

DCAMWAIT_CAPEVENT_FRAMEREADY = int("0x0002", 0)
DCAMWAIT_CAPEVENT_STOPPED = int("0x0010", 0)

DCAMWAIT_RECEVENT_MISSED = int("0x00000200", 0)
DCAMWAIT_RECEVENT_STOPPED = int("0x00000400", 0)
DCAMWAIT_TIMEOUT_INFINITE = int("0x80000000", 0)

DCAM_DEFAULT_ARG = 0

DCAM_IDSTR_MODEL = int("0x04000104", 0)

DCAMCAP_TRANSFERKIND_FRAME = 0

DCAMCAP_START_SEQUENCE = -1
DCAMCAP_START_SNAP = 0

DCAMBUF_ATTACHKIND_FRAME = 0

# Hamamatsu structures.

## DCAMAPI_INIT
#
# The dcam initialization structure
#
class DCAMAPI_INIT(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32), 
            ("iDeviceCount", ctypes.c_int32),
            ("reserved", ctypes.c_int32),
            ("initoptionbytes", ctypes.c_int32),
            ("initoption", ctypes.POINTER(ctypes.c_int32)),
            ("guid", ctypes.POINTER(ctypes.c_int32))]

## DCAMDEV_OPEN
#
# The dcam open structure
#
class DCAMDEV_OPEN(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("index", ctypes.c_int32),
            ("hdcam", ctypes.c_void_p)]


## DCAMWAIT_OPEN
#
# The dcam wait open structure
#
class DCAMWAIT_OPEN(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("supportevent", ctypes.c_int32),
            ("hwait", ctypes.c_void_p),
            ("hdcam", ctypes.c_void_p)]

## DCAMWAIT_START
#
# The dcam wait start structure
#
class DCAMWAIT_START(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("eventhappened", ctypes.c_int32),
            ("eventmask", ctypes.c_int32),
            ("timeout", ctypes.c_int32)]

## DCAMCAP_TRANSFERINFO
#
# The dcam capture info structure
#
class DCAMCAP_TRANSFERINFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iKind", ctypes.c_int32),
            ("nNewestFrameIndex", ctypes.c_int32),
            ("nFrameCount", ctypes.c_int32)]


## DCAMBUF_ATTACH
#
# The dcam buffer attachment structure
#
class DCAMBUF_ATTACH(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32), 
            ("iKind", ctypes.c_int32),
            ("buffer", ctypes.POINTER(ctypes.c_void_p)),
            ("buffercount", ctypes.c_int32)]

## DCAMBUF_FRAME
#
# The dcam buffer frame structure
#
class DCAMBUF_FRAME(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32), 
            ("iKind", ctypes.c_int32),
            ("option", ctypes.c_int32),
            ("iFrame", ctypes.c_int32),
            ("buf", ctypes.c_void_p),
            ("rowbytes", ctypes.c_int32),
            ("type", ctypes.c_int32),
            ("width", ctypes.c_int32),
            ("height", ctypes.c_int32),
            ("left", ctypes.c_int32),
            ("top", ctypes.c_int32),
            ("timestamp", ctypes.c_int32),
            ("framestamp", ctypes.c_int32),
            ("camerastamp", ctypes.c_int32)]


## DCAMDEV_STRING
#
# The dcam device string structure
#
class DCAMDEV_STRING(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32), 
            ("iString", ctypes.c_int32),
            ("text", ctypes.c_char_p),
            ("textbytes", ctypes.c_int32)]


## DCAMPROP_ATTR
#
# The dcam property attribute structure.
#
class DCAMPROP_ATTR(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("option", ctypes.c_int32),
                ("iReserved1", ctypes.c_int32),
                ("attribute", ctypes.c_int32),
                ("iGroup", ctypes.c_int32),
                ("iUnit", ctypes.c_int32),
                ("attribute2", ctypes.c_int32),
                ("valuemin", ctypes.c_double),
                ("valuemax", ctypes.c_double),
                ("valuestep", ctypes.c_double),
                ("valuedefault", ctypes.c_double),
                ("nMaxChannel", ctypes.c_int32),
                ("iReserved3", ctypes.c_int32),
                ("nMaxView", ctypes.c_int32),
                ("iProp_NumberOfElement", ctypes.c_int32),
                ("iProp_ArrayBase", ctypes.c_int32),
                ("iPropStep_Element", ctypes.c_int32)]

## DCAMPROP_VALUETEXT
#
# The dcam text property structure.
#
class DCAMPROP_VALUETEXT(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("value", ctypes.c_double),
                ("text", ctypes.c_char_p),
                ("textbytes", ctypes.c_int32)]

class DCAMREC_OPEN(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
                ("reserved", ctypes.c_int32),
                ("hrec", ctypes.c_void_p),
                ("path", ctypes.c_wchar_p),
                ("ext", ctypes.c_wchar_p),
                ("maxframepersession", ctypes.c_int32),
                ("userdatasize", ctypes.c_int32),
                ("userdatasize_session", ctypes.c_int32),
                ("userdatasize_file", ctypes.c_int32),
                ("usertextsize", ctypes.c_int32),
                ("usertextsize_session", ctypes.c_int32),
                ("usertextsize_file", ctypes.c_int32)]

class DCAMREC_STATUS(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
                ("currentsession_index", ctypes.c_int32),
                ("maxframecount_per_session", ctypes.c_int32),
                ("currentframe_index", ctypes.c_int32),
                ("missingframe_count", ctypes.c_int32),
                ("flags", ctypes.c_int32),
                ("totalframecount", ctypes.c_int32),
                ("reserved", ctypes.c_int32)]
    
def convertPropertyName(p_name):
    """
    "Regularizes" a property name. We are using all lowercase names with
    the spaces replaced by underscores.
    """
    return p_name.lower().replace(" ", "_")


class DCAMException(halExceptions.HardwareException):
    pass

class HCamData(object):
    None

class HamamatsuCamera(object):

    def __init__(self, camera_id = None, **kwds):
        None


    def __captureSetup(self):
        None


    def checkStatus(self, fn_return, fn_name= "unknown"):
        None

    def getCameraProperties(self):
        None

    def getFrames(self):
        None

    def getModelInfo(self, camera_id):
        None

    def getProperties(self):
        None

    def getPropertyAttribute(self, property_name):
        None

    def getPropertyRange(self, property_name):
        None

    def getPropertyRW(self, property_name):
        None

    def getPropertyText(self, property_name):
        None

    def getPropertyValue(self, property_name):
        None
    
    def getPropertiesValues(self):
        None

    def isCameraProperty(self, property_name):
        None

    def newFrames(self):
        None

    def setPropertyValue(self, property_name, property_value):
        None

    def setSubArrayMode(self):
        None

    def setACQMode(self, mode, number_frames = None):
        None

    def startAcquisition(self):
        None

    def stopAcquisition(self):
        None

    def shutdown(self):
        None

    def sortedPropertyTextOptions(self, property_name):
        None


class HamamatsuCameraMR(HamamatsuCamera):

    def __init__(self, **kwds):
        None

    def getFrames(self):
        frames = []
        return [frames, [None, None]]

    def startAcquisition(self):
        None


    def stopAcquisition(self):
        None
    
    def startRecording(self):
        None
        



if __name__ == '__main__':
    
    import sys
    import pyqtgraph as pg
    import qtpy
    from qtpy.QtWidgets import QApplication
    
    
    #
    # Initialization
    #
    #dcam = ctypes.WinDLL('C:\\Users\\Admin\\Downloads\\DCAM-API for Windows (18.11.5660)\\DCAMAPI\\fbdphx\\Win\\x64\\dcamapi.dll')
    dcam = ctypes.windll.dcamapi
    #dcam.visit()
    print(dcam)
    paraminit = DCAMAPI_INIT(0, 0, 0, 0, None, None) 
    paraminit.size = ctypes.sizeof(paraminit)
    error_code = dcam.dcamapi_init(ctypes.byref(paraminit))
    if (error_code != DCAMERR_NOERROR):
        raise DCAMException("DCAM initialization failed with error code " + str(error_code))
    
    n_cameras = paraminit.iDeviceCount

    print("found: {} cameras".format(n_cameras))
    hcam = HamamatsuCameraMR(camera_id = 0)
    print("camera 0 model:", hcam.getModelInfo(0))

    
    
    
    
    
    
#     what = hcam.getProperties()
#     print(what)
#     attr = hcam.getPropertyAttribute('sensor_mode')
#     print(attr.valuemax)
#     rang = hcam.getPropertyRange('image_framebytes')
#     print(rang)
#     ragn = hcam.setPropertyValue('exposure_time', 0.01)
#     print(ragn)
#     boh = hcam.getPropertyValue('exposure_time')
#     print(boh)
#     mboh = hcam.getPropertyRW('image_framebytes')
#     print(mboh)
#     
#     mboh = hcam.getPropertyAttribute('subarray_hsize')
#     print(mboh.valuemax)
#     mboh = hcam.setPropertyValue('subarray_hsize', mboh.valuemin )
#     print(mboh)
#     mboh = hcam.getPropertyAttribute('subarray_vsize')
#     print(mboh.attribute , bin(mboh.attribute))
#     print(mboh.attribute & DCAMPROP_ATTR_WRITABLE)
#     mboh = hcam.setPropertyValue('subarray_vsize', mboh.valuemin)
#     hcam.getPropertiesValues()
#     rang = hcam.getPropertyValue('image_framebytes')
#     print(rang)
#     
#     image = hcam.setPropertyValue("subarray_mode", "ON")
#     print(image)
#     rang = hcam.getPropertyValue('image_framebytes')
#     print(rang)

    
    hcam.number_frames = 1
    hcam.acquisition_mode = "fixed_length"
    hsize = int(hcam.setPropertyValue("subarray_hsize", 2048))#int is for the reshape function(see later)
    vsize = int(hcam.setPropertyValue("subarray_vsize", 2048))
    hoffset = hcam.setPropertyValue("subarray_hpos", 0)
    voffset = hcam.setPropertyValue("subarray_vpos", 0)
    mode = hcam.setPropertyValue("subarray_mode", "ON")
    exposure = hcam.setPropertyValue("exposure_time", 0.1) #when changing the exposure time, remember there is a timeout for the wait event 
    binning = hcam.setPropertyValue("binning", "1x1")
#   trigger
#   trsource=hcam.setPropertyValue("trigger_source", DCAMPROP_TRIGGERSOURCE__EXTERNAL) 
#   trmode=hcam.setPropertyValue("trigger_mode", DCAMPROP_TRIGGER_MODE__START)
#   trpolarity=hcam.setPropertyValue("trigger_polarity", DCAMPROP_TRIGGERPOLARITY__POSITIVE)
    #bin_fp = open("D://Data//trying_acquisition.dcimg", "wb")
    props = hcam.getPropertiesValues()
    print(props)
    
    while hcam.getPropertyValue("sensor_temperature")[0] > -9.0:
        pass
    #if 1:
    #bin_fp = open("e:/zhuang/test.bin", "wb")
    if 0:
        
        hcam.startAcquisition()
        print("Gooooo")
        time.sleep(5)
        for i in range(hcam.number_frames):
    
            # Get frames.
            [frames, dims] = hcam.getFrames()
    
            # Save frames.
            for aframe in frames:
                np_data = aframe.getData()
                pg.image(np.reshape(np_data,(vsize, hsize)).T,)
                #np_data.tofile(bin_fp)
    
            # Print backlog.
            print (i, len(frames))
            #print(np_data)
            #pg.image(np.reshape(np_data,(vsize, hsize)).T) #.T do the transpose, otherwise the image is inverted (due to how data are put in the buffer)
            #if (len(frames) > 20):
            #    exit()
    
        hcam.stopAcquisition()
        #bin_fp.close()
        hcam.shutdown()
        error_uninit = dcam.dcamapi_uninit()
        
        if (error_uninit != DCAMERR_NOERROR):
            raise DCAMException("DCAM uninitialization failed with error code " + str(error_uninit))
    
    if 1:
        try:
            
            hcam.startRecording()
            
        
        finally:
            
            dcam.dcamcap_stop(hcam.camera_handle)

            error_uninit = dcam.dcamapi_uninit()
            
            if (error_uninit != DCAMERR_NOERROR):
                raise DCAMException("DCAM uninitialization failed with error code " + str(error_uninit))
        

    if sys.flags.interactive !=1 or not hasattr(qtpy.QtCore, 'PYQT_VERSION'):
            QApplication.exec_()
    
    
    
    
    
    #start = hcam.startAcquisition()

#     start = hcam.startAcquisition()
#     stop = hcam.stopAcquisition()
#    print(start, stop)
# Testing.
#
# if (__name__ == "__main__"):
# 
#     import time
#     import random
# 
#     print("found:", n_cameras, "cameras")
#     if (n_cameras > 0):
# 
#         hcam = HamamatsuCameraMR(camera_id = 0)
#         print(hcam.setPropertyValue("defect_correct_mode", 1))
#         print("camera 0 model:", hcam.getModelInfo(0))
# 
#         # List support properties.
#         if False:
#             print("Supported properties:")
#             props = hcam.getProperties()
#             for i, id_name in enumerate(sorted(props.keys())):
#                 [p_value, p_type] = hcam.getPropertyValue(id_name)
#                 p_rw = hcam.getPropertyRW(id_name)
#                 read_write = ""
#                 if (p_rw[0]):
#                     read_write += "read"
#                 if (p_rw[1]):
#                     read_write += ", write"
#                 print("  ", i, ")", id_name, " = ", p_value, " type is:", p_type, ",", read_write)
#                 text_values = hcam.getPropertyText(id_name)
#                 if (len(text_values) > 0):
#                     print("          option / value")
#                     for key in sorted(text_values, key = text_values.get):
#                         print("         ", key, "/", text_values[key])

#         # Test setting & getting some parameters.
#         if False:
#             print(hcam.setPropertyValue("exposure_time", 0.001))
# 
#             #print(hcam.setPropertyValue("subarray_hsize", 2048))
#             #print(hcam.setPropertyValue("subarray_vsize", 2048))
#             print(hcam.setPropertyValue("subarray_hpos", 512))
#             print(hcam.setPropertyValue("subarray_vpos", 512))
#             print(hcam.setPropertyValue("subarray_hsize", 1024))
#             print(hcam.setPropertyValue("subarray_vsize", 1024))
# 
#             print(hcam.setPropertyValue("binning", "1x1"))
#             print(hcam.setPropertyValue("readout_speed", 2))
#     
#             hcam.setSubArrayMode()
#             #hcam.startAcquisition()
#             #hcam.stopAcquisition()
# 
#             params = ["internal_frame_rate",
#                       "timing_readout_time",
#                       "exposure_time"]
# 
#             #                      "image_height",
#             #                      "image_width",
#             #                      "image_framebytes",
#             #                      "buffer_framebytes",
#             #                      "buffer_rowbytes",
#             #                      "buffer_top_offset_bytes",
#             #                      "subarray_hsize",
#             #                      "subarray_vsize",
#             #                      "binning"]
#             for param in params:
#                 print(param, hcam.getPropertyValue(param)[0])
# 
#         # Test 'run_till_abort' acquisition.
#         if False:
#             print("Testing run till abort acquisition")
#             hcam.startAcquisition()
#             cnt = 0
#             for i in range(300):
#                 [frames, dims] = hcam.getFrames()
#                 for aframe in frames:
#                     print(cnt, aframe[0:5])
#                     cnt += 1
# 
#             print("Frames acquired: " + str(cnt))    
#             hcam.stopAcquisition()
# 
#         # Test 'fixed_length' acquisition.
#         if True:
#             for j in range (10000):
#                 print("Testing fixed length acquisition")
#                 hcam.setACQMode("fixed_length", number_frames = 10)
#                 hcam.startAcquisition()
#                 cnt = 0
#                 iterations = 0
#                 while cnt < 11 and iterations < 20:
#                     [frames, dims] = hcam.getFrames()
#                     waitTime = random.random()*0.03
#                     time.sleep(waitTime)
#                     iterations += 1
#                     print('Frames loaded: ' + str(len(frames)))
#                     print('Wait time: ' + str(waitTime))
#                     for aframe in frames:
#                         print(cnt, aframe[0:5])
#                         cnt += 1
#                 if cnt < 10:
#                     print('##############Error: Not all frames found#########')
#                     input("Press enter to continue")
#                 print("Frames acquired: " + str(cnt))        
#                 hcam.stopAcquisition()
# 
#                 hcam.setACQMode("run_till_abort")
#                 hcam.startAcquisition()
#                 time.sleep(random.random())
#                 contFrames = hcam.getFrames()
#                 hcam.stopAcquisition()



#
# The MIT License
#
# Copyright (c) 2013 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
