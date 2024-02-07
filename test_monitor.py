from psychopy import core, event, visual, monitors
import numpy as np


gammaGrid = np.array([  [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ]], dtype=float)

resolution = [640, 320]
size = [59.8, 33.6]
distance = 50


mymonitor = monitors.Monitor(name='temp',
                             distance=distance,
                             width=size[0])
mymonitor.setGammaGrid(gammaGrid)
mymonitor.setSizePix(resolution)

# win = visual.Window(resolution,allowGUI=True, monitor=mymonitor, units='deg', viewPos = [13,0], fullscr = False, color=[.5,-1,.5])
mywin = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', fullscr = False, color=[-0.5,-0.5,-0.5], screen=1) # back to same lay-out as in blindspot mapping task, to keep stuff really aligned

# mywin = visual.Window()

# myET = EyeTracker(tracker='livetrack', 
#                   fixationWindow=2, 
#                   trackEyes=[True, True], 
#                   psychopyWindow=mywin)

# myET.initialize()

# myET.calibrate()

# #myET.__np.sin(2) # this does not work

# mywin.close()