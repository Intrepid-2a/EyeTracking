#LiveTrack.py
# version 2.0 for Python3

# Copyright 2018 Cambridge Research Systems Ltd.
#
# Used to communicate with a LiveTrack device.
#

import ctypes
import sys
import os
try:
    if sys.platform == 'win32': # if Windows
        print('Using Windows')
        libPath = "C:\\Program Files\\Cambridge Research Systems\\LiveTrack Viewer\\libLiveTrack.dll"
        if not os.path.isfile(libPath):
            libPath = "C:\\Program Files (x86)\\Cambridge Research Systems\\LiveTrack Viewer x86\\libLiveTrack.dll"
        _dll = ctypes.CDLL(libPath)
    elif sys.platform.startswith('linux'): # if Linux
        print('Using Linux')
        _dll = ctypes.CDLL('/usr/lib/libLiveTrack.so')
    elif sys.platform == 'darwin': # if Mac OS X
        print('Using Mac OS X')
        _dll = ctypes.CDLL('/usr/local/lib/libLiveTrack.dylib')
    else:
        raise Exception('OS not supported! Must be Windows or Linux.')
except:
    raise Exception('Error loading Library. Please check if the file path is correct')


class T_RESULTS_STRUCT(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Size", ctypes.c_ushort),
        ("Timestamp", ctypes.c_ulonglong),
        ("ResultsType", ctypes.c_ushort),
        ("ActiveROIs", ctypes.c_uint),
        ("GlintX", ctypes.c_float),
        ("GlintY", ctypes.c_float),
        ("PupilX", ctypes.c_float),
        ("PupilY", ctypes.c_float),
        ("PupilMajorAxis", ctypes.c_float),
        ("PupilMinorAxis", ctypes.c_float),
        ("VectX", ctypes.c_float),
        ("VectY", ctypes.c_float),
        ("GazeX", ctypes.c_float),
        ("GazeY", ctypes.c_float),
        ("GazeZ", ctypes.c_float),
        ("GazeAzimuth", ctypes.c_float),
        ("GazeElevation", ctypes.c_float),
        ("GazeLongitude", ctypes.c_float),
        ("GazeLatitude", ctypes.c_float),
        ("Tracked", ctypes.c_byte),
        ("Enabled", ctypes.c_byte),
        ("Calibrated", ctypes.c_byte),
        ("Dropped", ctypes.c_byte),
        ("ROI", ctypes.c_byte),
        ("ActiveROIsRight", ctypes.c_uint),
        ("GlintXRight", ctypes.c_float),
        ("GlintYRight", ctypes.c_float),
        ("PupilXRight", ctypes.c_float),
        ("PupilYRight", ctypes.c_float),
        ("PupilMajorAxisRight", ctypes.c_float),
        ("PupilMinorAxisRight", ctypes.c_float),
        ("VectXRight", ctypes.c_float),
        ("VectYRight", ctypes.c_float),
        ("GazeXRight", ctypes.c_float),
        ("GazeYRight", ctypes.c_float),
        ("GazeZRight", ctypes.c_float),
        ("GazeAzimuthRight", ctypes.c_float),
        ("GazeElevationRight", ctypes.c_float),
        ("GazeLongitudeRight", ctypes.c_float),
        ("GazeLatitudeRight", ctypes.c_float),
        ("TrackedRight", ctypes.c_byte),
        ("EnabledRight", ctypes.c_byte),
        ("CalibratedRight", ctypes.c_byte),
        ("DroppedRight", ctypes.c_byte),
        ("ROIRight", ctypes.c_byte),
        ("DigitalIO", ctypes.c_uint),
        ("FixationDetected", ctypes.c_byte)]
        
class targ_struct(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Target_X", ctypes.c_double),
        ("Target_Y", ctypes.c_double),
        ("Vector_X", ctypes.c_double),
        ("Vector_Y", ctypes.c_double)]

def Init():
    print('LiveTrack: Initialising device...')
    deviceType= _dll.crsLiveTrackInit()
    if deviceType<1:
        print('ERROR: LiveTrack device not found! Is the data interface (HID) still connected to the LiveTrack Viewer App? Close the app or detach the data interface')
    if deviceType==1:
        print('LiveTrack FM initialised.')
    elif deviceType==2:
        print('LiveTrack AP initialised.')
    elif deviceType==3:
        print('LiveTrack AV initialised.')
    elif deviceType==4:
        print('LiveTrack Presto initialised.')
    else:
        print('LiveTrack: Unknown device type found')
    return deviceType

def Close():
    result= _dll.crsLiveTrackClose()
    if result==0:
        print('LiveTrack: Successfully closed device')
    else:
        print('LiveTrack: Error closing device')
    return result

def GetFirmwareVersion():
    version = ctypes.c_ushort()
    result = _dll.crsLiveTrackGetFirmwareVersion(ctypes.byref(version))
    if result!=0:
        print( 'LiveTrack: Error getting firmware version')
    return version.value
    
def GetLibraryVersion():
    version = _dll.crsLiveTrackGetLibVersion()
    if version==0:
        print('LiveTrack: Error getting library version')
    return version
    
def GetSerialNumber():
    serial = ctypes.create_string_buffer(16)
    result = _dll.crsLiveTrackGetSerialNumber(ctypes.byref(serial), 16)
    if result!=0:
        print('LiveTrack: Error getting serial number')
    return serial.value

def GetLastResult():
    data = T_RESULTS_STRUCT(0)
    result = _dll.crsLiveTrackGetLastResult(ctypes.byref(data))
    if result!=0:
        print( 'LiveTrack: Error Getting last result')
    return data
	
def GetTracking():
    leftEye = ctypes.c_bool()
    rightEye = ctypes.c_bool()
    result = _dll.crsLiveTrackGetTracking(ctypes.byref(leftEye),ctypes.byref(rightEye))
    if result!=0:
        print('LiveTrack: Error Getting tracking status')
    return leftEye.value, rightEye.value

def SetTracking(leftEye,rightEye):
    result = _dll.crsLiveTrackSetTracking(bool(leftEye), bool(rightEye))
    if result!=0:
        print('LiveTrack: Error setting tracking status')
    else:
        print('LiveTrack: Tracking status set successfully')
    return result

def ClearDataBuffer():
    result= _dll.crsLiveTrackClearDataBuffer()
    if result==0:
        print('LiveTrack: Data buffer cleared')
    else:
        print('LiveTrack: Error clearing LiveTrack data buffer')
    return result

def GetResultsCount():
    count = _dll.crsLiveTrackGetResultsCount()
    if count<0:
        print('LiveTrack: Error Getting results count')
    return count

def StartTracking():
    result = _dll.crsLiveTrackStartTracking()
    if result!=0:
        print('LiveTrack: Error starting tracking')
    else:
        print('LiveTrack: Started tracking')
    return result

def StopTracking():
    result = _dll.crsLiveTrackStopTracking()
    if result!=0:
        print('LiveTrack: Error stopping tracking')
    else:
        print('LiveTrack: Stopped tracking')
    return result

def GetBufferedEyePositions(removeFromBuffer=1,maximumPoints=-1,fromBeginning=1):
    # get number of results/samples in the buffer
    count = _dll.crsLiveTrackGetResultsCount()
    # check if requested amount of samples is valid
    if maximumPoints==-1 or maximumPoints>count:
        maximumPoints = count    
    # by default, set the pointer to the first result in the buffer   
    if fromBeginning:
        _dll.crsLiveTrackSetBufferPosition(0);
    else:
    # otherwise set the pointer to retreive the last samples in the buffer  
        _dll.crsLiveTrackSetBufferPosition(int(count-maximumPoints));    
    dataArray = []
    if maximumPoints>0:
        for x in range(0, int(maximumPoints)):
            data = T_RESULTS_STRUCT()
            # get the sample from the buffer and remove that sample
            result = _dll.crsLiveTrackGetBufferedResult(ctypes.byref(data), removeFromBuffer)
            if result == 0:
                dataArray.append(data)
            else:    
                print('LiveTrack: Error Getting buffered results')
    else:
        print('LiveTrack: No samples in buffer')
    return dataArray
    
def SetPupilCalibration(diameter, pixels):
    result = _dll.crsLiveTrackSetPupilCalibration(ctypes.c_double(diameter), ctypes.c_double(pixels))
    if result!=0:
        print('LiveTrack: Error setting pupil calibration')
    else:
        print('LiveTrack: pupil calibration set successfully')
    return result
    
def GetPupilCalibration():
    pixelsToMM = ctypes.c_double()
    result = _dll.crsLiveTrackGetPupilCalibration(ctypes.byref(pixelsToMM))
    if result!=0:
        print('LiveTrack: Error getting pupil calibration')
    else:
        print('LiveTrack: Got pupil calibration successfully')
    return pixelsToMM.value
    
def SetCalibration(eye, cal, viewDist, xGlintMedian, yGlintMedian):
    arr = (ctypes.c_double * len(cal))(*cal)
    result = _dll.crsLiveTrackSetCalibration(ctypes.c_int(eye), arr, ctypes.c_double(100), ctypes.c_double(viewDist), ctypes.c_double(xGlintMedian), ctypes.c_double(yGlintMedian))
    if result!=0:
        print('LiveTrack: Error setting calibration')
    else:
        print('LiveTrack: calibration set successfully')
    return result
    
def GetCalibration(eye):
    cal = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    arr = (ctypes.c_double * len(cal))(*cal)
    rpc = ctypes.c_double()
    viewDist = ctypes.c_double()
    xGlintMedian = ctypes.c_double()
    yGlintMedian = ctypes.c_double()
    result = _dll.crsLiveTrackGetCalibration(ctypes.c_int(eye), ctypes.byref(arr), ctypes.byref(rpc), ctypes.byref(viewDist), ctypes.byref(xGlintMedian), ctypes.byref(yGlintMedian))
    if result!=0:
        print('LiveTrack: Error getting calibration')
    else:
        print('LiveTrack: Got calibration successfully')
    return list(arr),  viewDist.value, xGlintMedian.value, yGlintMedian.value
    
def SetResultsTypeCalibrated():
    result = _dll.crsLiveTrackSetResultsType(ctypes.c_int(1))
    if result!=0:
        print('LiveTrack: Error setting result type to calibrated')
    else:
        print('LiveTrack: Successfully set result type to calibrated')
    return result
    
def SetResultsTypeRaw():
    result = _dll.crsLiveTrackSetResultsType(ctypes.c_int(0))
    if result!=0:
        print('LiveTrack: Error setting result type to raw')
    else:
        print('LiveTrack: Successfully set result type to raw')
    return result
    
def CalibrateDevice(eye, numberOfFixationTargets, targetsX, targetsY, vectX, vectY, viewDist, xGlintMedian=0, yGlintMedian=0):
    target_array_type = (targ_struct * numberOfFixationTargets)
    target = target_array_type()
    for i in range(0, numberOfFixationTargets):
        target[i].Target_X = targetsX[i]
        target[i].Target_Y = targetsY[i]
        target[i].Vector_X = vectX[i]
        target[i].Vector_Y = vectY[i]
    calErr = ctypes.c_int()
    result = _dll.crsLiveTrackCalibrateDevice(ctypes.c_int(eye), ctypes.c_uint(numberOfFixationTargets), target, ctypes.c_double(100), ctypes.c_double(viewDist), ctypes.c_double(xGlintMedian), ctypes.c_double(yGlintMedian), ctypes.byref(calErr));
    if result!=0:
        print('LiveTrack: Error calibrating device')
    else:
        print('LiveTrack: Successfully calibrated device')
    return calErr.value
    
def SaveCalibration(filename):
    namebuf = ctypes.create_unicode_buffer(filename, 512)
    result = _dll.crsLiveTrackSaveCalibration(ctypes.byref(namebuf))
    if result!=0:
        print('LiveTrack: Error saving calibration')
    else:
        print('LiveTrack: Successfully saved calibration')
    return result
    
def LoadCalibration(filename):
    namebuf = ctypes.create_unicode_buffer(filename, 512)
    result = _dll.crsLiveTrackLoadCalibration(ctypes.byref(namebuf))
    if result!=0:
        print('LiveTrack: Error loading calibration')
    else:
        print('LiveTrack: Successfully loaded calibration')
    return result
    
def CalcGaze(eye, numberOfGazePoints, vectX, vectY):
    gazeX = ctypes.c_double()
    gazeY = ctypes.c_double()
    result = _dll.crsLiveTrackGetCaptureConfig(ctypes.c_int(eye), ctypes.c_uint(numberOfGazePoints), ctypes.c_double(vectX), ctypes.c_double(vectY), ctypes.byref(gazeX), ctypes.byref(gazeY))
    if result!=0:
        print('LiveTrack: Error calculating gaze')
    return gazeX.value, gazeY.value

def GetCaptureConfig():
    width = ctypes.c_uint()
    height = ctypes.c_uint()
    rate = ctypes.c_uint()
    offsetX = ctypes.c_uint()
    offsetY = ctypes.c_uint()
    result = _dll.crsLiveTrackGetCaptureConfig(ctypes.byref(width), ctypes.byref(height), ctypes.byref(rate), ctypes.byref(offsetX), ctypes.byref(offsetY))
    if result!=0:
        print('LiveTrack: Error getting capture configuration')
    else:
        print('LiveTrack: Successfully got capture configuration')
    return width.value, height.value, rate.value, offsetX.value, offsetY.value
    
def GetFieldAsList(data, field_name):
    dataOut = []
    for x in range(0, len(data)):
        dataOut.append(getattr(data[x], field_name))
    return dataOut

def SetDataFilename(filename):
    filename8 = filename.encode('utf-8')
    namebuf = ctypes.create_string_buffer(filename8, 512)
    result = _dll.crsLiveTrackSetDataFilename(ctypes.byref(namebuf))
    if result!=0:
        print('LiveTrack: Error setting data filename')
    else:
        print('LiveTrack: Successfully set data filename')
    return result

def CloseDataFile():
    result = _dll.crsLiveTrackCloseDataFile()
    if result!=0:
        print('LiveTrack: Error Closing data file')
    else:
        print('LiveTrack: Closed data file')
    return result

def SetDataComment(comment):
    comment8 = comment8.encode('utf-8')
    namebuf = ctypes.create_string_buffer(comment8, 512)
    result = _dll.crsLiveTrackSetDataComment(ctypes.byref(namebuf))
    if result!=0:
        print('LiveTrack: Error setting data comment')
    else:
        print('LiveTrack: Successfully set data comment')
    return result

