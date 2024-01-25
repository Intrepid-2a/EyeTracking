import sys
import warnings
import numbers

# to test if input objects are valid psychopy classes:
import psychopy
# mouse dummy needs a psychopy.event.mouse object
# calibration requires a psychopy.visual.Window
# and psychopy.visual.*Stim (circleStim?)
from psychopy import core, event, visual


# this file has just 1 object that is needed: EyeTracker
# for now, it can be used as:
# -  from EyeTracker import EyeTracker
# -  myEyeTracker = EyeTracker(tracker='LiveTrack', trackEyes=[True,True], fixationWindow=2, psychopyWindow=cfg['hw']['win'])
# I could set up the folder to work like a proper Python module later where that is taken care of


class EyeTracker:

    def __init__(self, tracker=None, trackEyes=[False, False], fixationWindow=None, psychopyWindow=None):

        # these three function check the user input,
        # and store it for future use
        # they can also be used later on to change how the object works
        # and they are device-agnostic

        self.setEyetracker(tracker)
        self.trackEyes(trackEyes)
        self.setFixationWindow(fixationWindow)
        self.setPsychopyWindow(psychopyWindow)
        

    def setEyetracker(self, tracker):
        if isinstance(tracker, str):
            if tracker in ['eyelink', 'livetrack', 'mouse']:

                if tracker == 'eyelink':
                    # set up the eyelink device here
                    self.setupEyeLink()

                if tracker == 'livetrack':
                    # set up the livetrack device here
                    self.setupLiveTrack()

                if tracker == 'mouse':
                    # not sure what to do here
                    self.setupMouse()

                self.tracker = tracker
            else:
                raise Warning("unkown eye-tracker: %s"%(tracker))
        else:
            raise Warning("tracker must be a string")

    def trackEyes(self, trackEyes):
        if isinstance(trackEyes, list):
            if len(trackEyes) == 2:
                if all([isinstance(x, bool) for x in trackEyes]):
                    self.trackEyes = trackEyes
                else:
                    raise Warning("trackEyes must be a list of booleans")
            else:
                raise Warning("trackEyes must be a list of length 2")
        else:
            raise Warning("trackEyes must be a list")

    def setFixationWindow(self, fixationWindow):
        if isinstance(fixationWindow, numbers.Number):
            if fixationWindow > 0:
                self.fixationWindow = fixationWindow
            else:
                raise Warning("fixationWindow must be larger than 0")
        else:
            raise Warning("fixationWindow must be a number")

    def setPsychopyWindow(self, psychopyWindow):
        if isinstance(psychopyWindow, psychopy.visual.window.Window):
            self.win = psychopyWindow
        else:
            raise Warning("psychopyWindow must by a psychopy Window")

    def setupEyeLink(self):
        import pylink
        self.pylink = pylink

        # remap functions:
        self.initialize = self.__EL_initialize
        # ...
        # here we map other functions
        # ...

    def setupLiveTrack(self):
        import LiveTrack
        self.LiveTrack = LiveTrack

        # remap functions:
        self.initialize = self.__LT_initialize
        # ...
        # here we map other functions
        # ...

    def setupMouse(self):
        # this will be a psychopy mouse object
        import numpy as np
        self.__np = np

        # remap functions:
        self.initialize = self.__DM_initialize
        # ...
        # here we map other functions
        # ...


    # functions to initialize each device:
    # region

    def initialize(self):
        raise Warning("set a tracker before initializing it")

    def __EL_initialize(self):
        print('initialize EyeLink')

    def __LT_initialize(self):
        print('initialize LiveTrack')
        self.LiveTrack.Init()

        # Start LiveTrack using raw data (camera coords)
        self.LiveTrack.SetResultsTypeRaw()

        # Start buffering data
        self.LiveTrack.StartTracking()
        self.LiveTrack.SetTracking(leftEye=self.trackEyes[0],rightEye=self.trackEyes[1])

        # do calibration... this needs to be rewritten...
        # LTcal(cfg=cfg, trackLeftEye=trackLeftEye, trackRightEye=trackRightEye)

    def __DM_initialize(self):
        print('initialize dummy mouse')
        self.mouse = event.Mouse( visible = True,
                                  newPos = None,
                                  win = self.win )
        print(self.__np.sqrt(2))

    # endregion




    # the following functions should be different for each device:



    # at the start:    
    # def calibrate(self):
    # def savecalibration(self):

    # # during trials:
    # def lastsample(self):
    # def testfixation(self):
    # def comment(self):

    # # for breaks, and to switch to new files
    # # IIRC on the EyeLink you need to download files when you stopcollecting()?

    # def startcollecting(self):
    # def stopcollecting(self):

    # # at the end of the experiment:
    # def shutdown(self):

    
