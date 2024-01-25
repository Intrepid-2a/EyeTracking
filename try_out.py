from psychopy import core, event, visual
from EyeTracker import EyeTracker

mywin = visual.Window()

myET = EyeTracker(tracker='mouse', 
                  fixationWindow=2, 
                  trackEyes=[True, True], 
                  psychopyWindow=mywin)

myET.initialize()

#myET.__np.sin(2) # this does not work

mywin.close()