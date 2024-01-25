from psychopy import core, event, visual
from EyeTracker import EyeTracker

mywin = visual.Window()

myET = EyeTracker(tracker='mouse', 
                  fixationWindow=2, 
                  trackEyes=[True, True], 
                  psychopyWindow=mywin)

myET.initialize()

mywin.close()