from psychopy import core, event, visual, monitors
import numpy as np


gammaGrid = np.array([  [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ],
                        [  0., 1., 1., np.nan, np.nan, np.nan  ]], dtype=float)

resolution = [960, 540]
# resolution = [1920, 1080]
size = [29.8, 16.8]
# size = [59.8, 33.6]
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


resolution = mywin.monitor.getSizePix()
width      = mywin.monitor.getWidth()
distance   = mywin.monitor.getDistance()
gammaGrid  = mywin.monitor.getGammaGrid()

mymonitor = monitors.Monitor(name='EL_temp',
                             distance=distance,
                             width=width
                             )

mymonitor.setGammaGrid(gammaGrid)

screen = mywin.screen
color  = mywin.color

EL_window = win = visual.Window(resolution,
                                pos        = resolution,
                                monitor    = mymonitor, 
                                allowGUI   = True, 
                                units      = 'pix', 
                                fullscr    = False,
                                color      = color,
                                colorSpace = 'rgb', 
                                screen     = screen)

from psychopy.iohub.util import hideWindow, showWindow

hideWindow(EL_window)
showWindow(mywin)

hello = visual.TextStim(win = mywin, text='hello world!')

hello.draw()
mywin.flip()