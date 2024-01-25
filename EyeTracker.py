import sys
import warnings
import numbers

# we will also need to import libraries for both eyetrackers
# bit this will have to be done conditionally
# this is for EyeLink devices:
import pylink
# this is for LiveTrack devices:
import LiveTrack


class EyeTracker:

    def __init__(self, tracker=None, fixationWindow=None, trackEyes=[False, False]):

        self.setEyetracker(tracker)
        self.setFixationWindow(fixationWindow)
        self.trackEyes(trackEyes)

    def setEyetracker(self, tracker):
        if isinstance(tracker, str):
            if tracker in ['eyelink', 'livetrack', 'mouse']:
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


    # at the start:

    def initialize(self):
        if self.tracker in ['eyelink', 'livetrack', 'mouse']:
            if self.tracker == 'eyelink':
                self.initialize_eyelink()
            if self.tracker == 'livetrack':
                self.initialize_livetrack()
            if self.tracker == 'mouse':
                self.initialize_mouse()
        else:
            raise Warning("can not initialize tracker: %s"%(self.tracker))
    
    def calibrate(self):
    def savecalibration(self):

    # during trials:
    def lastsample(self):
    def testfixation(self):
    def comment(self):

    # for breaks, and to switch to new files
    # IIRC on the EyeLink you need to download files when you stopcollecting()?

    def startcollecting(self):
    def stopcollecting(self):

    # at the end of the experiment:
    def shutdown(self):
