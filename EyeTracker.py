import sys
import warnings
import numbers

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
                raise Warning("unkown eye-tracker")
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
