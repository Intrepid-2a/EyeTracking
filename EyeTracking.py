import sys
import warnings
import numbers
import numpy as np
import time
import math
import os
import json
import copy
import random

from glob import glob


# to test if input objects are valid psychopy classes:
import psychopy
# mouse dummy needs a psychopy.event.mouse object
# calibration requires a psychopy.visual.Window
# and psychopy.visual.*Stim (circleStim?)
from psychopy import core, event, visual, gui, monitors

from psychopy.tools import monitorunittools
from psychopy.hardware import keyboard
from pyglet.window import key

# import sys, os
# sys.path.append(os.path.join('..', 'EyeTracking'))
# from EyeTracking import EyeTracker



# this file has just 1 object that is needed: EyeTracker
# for now, it can be used as:
# -  from EyeTracker import EyeTracker
# -  myEyeTracker = EyeTracker(tracker='LiveTrack', trackEyes=[True,True], fixationWindow=2, psychopyWindow=cfg['hw']['win'])
# I could set up the folder to work like a proper Python module later where that is taken care of


class EyeTracker:

    def __init__(self, 
                 tracker=None, 
                 trackEyes=[False, False], 
                 fixationWindow=None,
                 minFixDur=None,
                 fixTimeout=None,
                 psychopyWindow=None, 
                 filefolder=None, 
                 filename=None,
                 samplemode=None,
                 calibrationpoints=5,
                 colors=None):


        # the functions below check the user input,
        # and store it for future use if OK
        # they can also be used later on to change how the object works
        # and are supposed to be device-agnostic

        self.setPsychopyWindow(psychopyWindow)
        self.setCalibrationpoints(calibrationpoints)
        self.setColors(colors)
        self.setEyetracker(tracker)
        self.trackEyes(trackEyes)
        self.setFixationWindow(fixationWindow)
        self.setMinFixDur(minFixDur)
        self.setFixTimeout(fixTimeout)
        self.setFilePath(filefolder, filename)
        self.setSamplemode(samplemode)


        # things below this comment are still up for change... depends a bit on how the EyeLink does things

        # maybe these should be a property that has a function to set it?
        # it's only used for the LiveTrack, so probably not...
        # self.__calibrationTargets = np.array([[0,0],   [-3,0],[0,3],[3,0],[0,-3],     [6,6],[6,-6],[-6,6],[-6,-6]])
        
        print(filefolder)
        print(filename)
        print(self.storefiles)
        
        self.__fileOpen = False
        self.__recording = False

        self.__EL_currentfile = ''
        self.__EL_downloadFiles = []

        self.__N_calibrations = 0
        self.__N_rawdatafiles = 0

        self.__createTargetStim()




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
                    if any(trackEyes):
                        self.trackEyes = trackEyes
                    else:
                        raise Warning("one or both eyes must be tracked")
                else:
                    raise Warning("trackEyes must only contain booleans")
            else:
                raise Warning("trackEyes must have length 2")
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

    def setMinFixDur(self, minFixDur):
        if isinstance(minFixDur, numbers.Number):
            if minFixDur > 0:
                self.minFixDur = minFixDur
            else:
                raise Warning("minimum fixation duration must be larger than 0")
        else:
            raise Warning("minimum fixation duration must be a number")


    def setFixTimeout(self, fixTimeout):
        if isinstance(fixTimeout, numbers.Number):
            if fixTimeout > self.minFixDur:
                self.fixTimeout = fixTimeout
            else:
                raise Warning("fixation timeout must be larger than minimum fixation duration")
        else:
            raise Warning("fixation timeout must be a number")



    def setPsychopyWindow(self, psychopyWindow):
        if isinstance(psychopyWindow, psychopy.visual.window.Window):
            if psychopyWindow.units == 'deg':
                self.psychopyWindow = psychopyWindow
            else:
                raise Warning("psychopyWindow must have units set to 'deg'")
        else:
            raise Warning("psychopyWindow must by a psychopy Window")


    def setFilePath(self, filefolder, filename):
        self.storefiles = False
        if isinstance(filefolder, str):
            if len(filefolder) > 0:
                # self.storefiles = False
                # check if it is an existing path
                if os.path.isdir(filefolder):
                    if isinstance(filename, str):
                        if len(filename) > 0:
                            # CHECK IF FILE ALREADY EXISTS?
                            self.storefiles  = True
                            self.filefolder  = filefolder
                            self.filename    = filename
                        else:
                            print('NOTE: not storing any data since filename is an empty string')
                    else:
                        print('NOTE: not storing any data since filename is not a string')
                else:
                    raise Warning("filefolder is not a valid or existing path: %s"%(filefolder))
            else:
                print('NOTE: not storing any files since filefolder is an empty string')
        else:
            print('NOTE: not storing any files since filefolder is not a string')
        

    def setSamplemode(self, samplemode):
        if isinstance(samplemode, str):
            if samplemode in ['both', 'left', 'right', 'average']:
                self.samplemode = samplemode
            else:
                raise Warning("unkown samplemode: %s"%(samplemode))
        else:
            raise Warning("samplemode must be a string")



    def setCalibrationpoints(self, calibrationpoints):
        if isinstance(calibrationpoints, numbers.Number):
            if calibrationpoints in [5,9]:
                # allowed number of points?
                self.calibrationpoints = calibrationpoints
                if calibrationpoints == 5:
                    self.__calibrationTargets = np.array([[0,0],   [-3,0],[0,3],[3,0],[0,-3]                                 ])
                if calibrationpoints == 9:
                    self.__calibrationTargets = np.array([[0,0],   [-3,0],[0,3],[3,0],[0,-3],     [6,6],[6,-6],[-6,6],[-6,-6]])
                # print(self.__calibrationTargets)
            else:
                raise Warning("calibration points muct be 9 (default) or 5")
        else:
            raise Warning("calibration points must be a number")


        # eyetracker_config['calibration'] = dict(type='THIRTEEN_POINTS')

    def setColors(self, colors):
        if isinstance(colors, dict):
            # no more checks for now, but should check that it has at least col_back: used for eyelink calibration...
            self.colors = colors
        else:
            raise Warning("colors should be a dictionary")


    def setupEyeLink(self):
        
        # python library to interface with EyeLink:
        # note, we should either use pylink or use the psychopy IOhub system: apparently, they can't be mixed
        # import pylink
        # self.pylink = pylink

        from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
        self.EyeLinkCoreGraphicsPsychoPy = EyeLinkCoreGraphicsPsychoPy


        # psychopy iohub stuff to make things a bit harder:
        from psychopy.iohub.client import launchHubServer
        self.launchHubServer = launchHubServer
        from psychopy.iohub.util import hideWindow, showWindow
        self.hideWindow = hideWindow
        self.showWindow = showWindow
        # does this showwindow/hidewindow stuff need to be applied/bound to an extra window?


        # constant to convert pixels to degrees for the case of the EyeLink only
        self.__EL_p2df = monitorunittools.pix2deg(1, self.psychopyWindow.monitor)
        self.__EL_offset = np.array([(x-1)/2 for x in self.psychopyWindow.monitor.getSizePix()])


        # EyeLink / IOhub needs a window object with the unit in pixels
        # but everything else needs degrees (including the LiveTrack calibration)
        # so for this exception, we create a new window, based on the input window:


            #     if location == 'glasgow':
            #     # not a calibrated monitor?
            #     gammaGrid = np.array([ [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
            #                         [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
            #                         [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
            #                         [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ]  ], dtype=float)

            #     resolution = [1920, 1080] # in pixels
            #     size       = [60, 33.75] # in cm
            #     distance   = 57 # in cm
            #     screen     = 0 # index on the system: 0 = first monitor, 1 = second monitor, and so on

            #     tracker = 'eyelink'


            # if location == 'toronto':
            #     # color calibrated monitor:
            #     gammaGrid = np.array([ [  0., 135.44739,  2.4203537, np.nan, np.nan, np.nan  ],
            #                         [  0.,  27.722954, 2.4203537, np.nan, np.nan, np.nan  ],
            #                         [  0.,  97.999275, 2.4203537, np.nan, np.nan, np.nan  ],
            #                         [  0.,   9.235623, 2.4203537, np.nan, np.nan, np.nan  ]  ], dtype=float)

            #     resolution = [1920, 1080] # in pixels
            #     size       = [59.8, 33.6] # in cm
            #     distance   = 50 # in cm
            #     screen     = 0  # index on the system: 0 = first monitor, 1 = second monitor, and so on

            #     tracker = 'livetrack'

            # mymonitor = monitors.Monitor(name='temp',
            #                             distance=distance,
            #                             width=size[0])
            # if location == 'toronto':
            #     mymonitor.setGammaGrid(gammaGrid)
            # mymonitor.setSizePix(resolution)

            # #win = visual.Window([1000, 500], allowGUI=True, monitor='ccni', units='deg', fullscr=True, color = back_col, colorSpace = 'rgb')
            # win = visual.Window(resolution, monitor=mymonitor, allowGUI=True, units='deg', fullscr=True, color=back_col, colorSpace = 'rgb', screen=screen)

        resolution = self.psychopyWindow.monitor.getSizePix()
        width      = self.psychopyWindow.monitor.getWidth()
        distance   = self.psychopyWindow.monitor.getDistance()

        mymonitor = monitors.Monitor(name='EL_temp',
                                     distance=distance,
                                     width=width
                                     )

        # leave out the whole gamma grid for now, it's not relevant at this point, maybe in the future?

        # gammaGrid  = self.psychopyWindow.monitor.getGammaGrid()
        # defaultGammaGrid = np.array([ [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
        #                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
        #                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
        #                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ]  ], dtype=np.float32)
        # if not np.array_equal(mymonitor.getGammaGrid()[:,:3], defaultGammaGrid[:,:3]):
        #     mymonitor.setGammaGrid(gammaGrid)

        screen = self.psychopyWindow.screen
        color  = self.psychopyWindow.color
        if hasattr(self, 'colors'):
            if 'back' in self.colors.keys():
                color = self.colors['back']
        else:
            # what is a sensible default?
            color = [0,0,0]
            print('No color attribute, using PsychoPy default background color.')

        self.__EL_window = win = visual.Window(resolution, 
                                               monitor    = mymonitor, 
                                               allowGUI   = True, 
                                               units      = 'pix', 
                                               fullscr    = True,
                                               color      = color,
                                               colorSpace = 'rgb', 
                                               screen     = screen)

        # remap functions:
        self.initialize = self.__EL_initialize
        self.calibrate  = self.__EL_calibrate
        self.savecalibration = self.__EL_savecalibration

        self.lastsample = self.__EL_lastsample

        self.openfile = self.__EL_openfile
        self.startcollecting = self.__EL_startcollecting
        self.stopcollecting = self.__EL_stopcollecting
        self.closefile = self.__EL_closefile

        self.comment = self.__EL_comment
        self.shutdown = self.__EL_shutdown
        # ...
        # here we map other functions
        # ...

    def setupLiveTrack(self):
        import LiveTrack
        self.LiveTrack = LiveTrack

        # remap functions:
        self.initialize = self.__LT_initialize
        self.calibrate  = self.__LT_calibrate
        self.savecalibration = self.__LT_savecalibration

        self.lastsample = self.__LT_lastsample

        self.openfile = self.__LT_openfile
        self.startcollecting = self.__LT_startcollecting
        self.stopcollecting = self.__LT_stopcollecting
        self.closefile = self.__LT_closefile

        self.comment = self.__LT_comment
        self.shutdown = self.__LT_shutdown
        # ...
        # here we map other functions
        # ...

    def setupMouse(self):
        # this will be a psychopy mouse object
        # import numpy as np
        # self.__np = np

        # remap functions:
        self.initialize = self.__DM_initialize
        self.calibrate  = self.__DM_calibrate
        self.savecalibration = self.__DM_savecalibration

        self.lastsample = self.__DM_lastsample

        self.openfile = self.__DM_openfile
        self.startcollecting = self.__DM_startcollecting
        self.stopcollecting = self.__DM_stopcollecting
        self.closefile = self.__DM_closefile

        self.comment = self.__DM_comment
        self.shutdown = self.__DM_shutdown
        # ...
        # here we map other functions
        # ...


    # functions to initialize each device:
    # region

    def initialize(self):
        raise Warning("set a tracker before initializing it")

    def __EL_initialize(self):
        # print('initialize EyeLink')

        # # new code for pylink:
        # self.EL = pylink.EyeLink('100.1.1.1')

        # # this is only for the data viewer:
        # message = 'DISPLAY_COORDS 0 0 %d %d'%(self.psychopyWindow.size[0]-1,self.psychopyWindow.size[1]-1) # unless we use a retina display on a mac?
        # self.EL.sendMessage(message)

        
        # # set to offline mode
        # self.EL.setOfflineMode()

        # # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
        # # 5-EyeLink 1000 Plus, 6-Portable DUO
        # eyelink_ver = 0  # set version to 0, in case running in Dummy mode
        # if not dummy_mode:
        #     vstr = self.EL.getTrackerVersionString()
        #     eyelink_ver = int(vstr.split()[-1].split('.')[0])
        #     # print out some version info in the shell
        #     print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

        # # File and Link data control
        # # what eye events to save in the EDF file, include everything by default
        # file_event_flags = '%sFIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'%(track_eyes)
        # # what eye events to make available over the link, include everything by default
        # link_event_flags = '%sFIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'%(track_eyes)
        # # what sample data to save in the EDF data file and to make available
        # # over the link, include the 'HTARGET' flag to save head target sticker
        # # data for supported eye trackers
        # if eyelink_ver > 3:
        #     file_sample_flags = '%sGAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'%(track_eyes)
        #     link_sample_flags = '%sGAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'%(track_eyes)
        # else:
        #     file_sample_flags = '%sGAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'%(track_eyes)
        #     link_sample_flags = '%sGAZE,GAZERES,AREA,STATUS,INPUT'%(track_eyes)
        # self.EL.sendCommand("file_event_filter = %s" % file_event_flags)
        # self.EL.sendCommand("file_sample_data = %s" % file_sample_flags)
        # self.EL.sendCommand("link_event_filter = %s" % link_event_flags)
        # self.EL.sendCommand("link_sample_data = %s" % link_sample_flags)


        # # we'll calibrate with a 9-point calibration:
        # self.EL.sendCommand("calibration_type = HV9")

        # # make the psychopy graphics environment available for calibrations:
        # self.genv = EyeLinkCoreGraphicsPsychoPy(self.EL, self.psychopyWindow)
        # print(self.genv)  # print out the version number of the CoreGraphics library

        # # Set background and foreground colors for the calibration target
        # # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
        # foreground_color = (-1, -1, -1)
        # background_color = self.psychopyWindow.color
        # self.genv.setCalibrationColors(foreground_color, background_color)

        # # no calibration sounds please:
        # self.genv.setCalibrationSounds('off', 'off', 'off')

        # # tell pylink to use the graphics environment:
        # self.pylink.openGraphicsEx(self.genv)


        # old code for iohub:

        # tell the eyelink which eyes to track
        # we'll store and make available the same eyes (this could be set up differently)
        track_eyes = None
        if all(self.trackEyes):
            # track_eyes = 'LEFT,RIGHT' # this line had a typoe, but also, it's not what Clement sent me earlier:
            track_eyes = 'BINOCULAR'
        else:
            # only one eye is tracked?
            if self.trackEyes[0]:
                track_eyes = 'LEFT_EYE'  # or just 'LEFT' ?
            if self.trackEyes[1]:
                track_eyes = 'RIGHT_EYE'  # or just 'RIGHT' ?
        # if no eye is tracked, that is going to be really hard for calibration and getting any samples...
        if track_eyes == None:
            raise Warning("trackEyes needs to set at least one eye to be tracked")


        # set up configuration for our particular EyeLink
        devices_config = dict()
        eyetracker_config = {'name':'tracker'}
        eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
        # eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, track_eyes='BOTH') # this line from Clement, but let's try the next one for now:
        eyetracker_config['runtime_settings'] = {'sampling_rate':1000, 'track_eyes':track_eyes}

        if self.storefiles:
            eyetracker_config['default_native_data_file_name'] = self.filename  # correct extention is added by IOhub
            eyetracker_config['local_edf_dir'] = self.filefolder                # otherwise this ends up in the main folder where the experiment itself lives
        # else:
        #     print('no eyelink files should be stored')
        #     eyetracker_config['default_native_data_file_name'] = ''  # correct extention is added by IOhub
        #     eyetracker_config['local_edf_dir'] = ''                  # otherwise this ends up in the main folder where the experiment itself lives

        # this calibration dictionary based on:
        # https://psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
        calibration = {
                       'auto_pace': True,
                       'pacing_speed': 1.5,
                       'target_type': 'CIRCLE_TARGET',
                       'target_attributes': {
                            'outer_diameter': 1.0 / self.__EL_p2df,
                            'inner_diameter': 0.2 / self.__EL_p2df,
                            'outer_color': [255,255,255,255],
                            'inner_color': [0,0,0,255]
                            }
                       }
        

        # inner diameter: 0.2 dva
        # outer diameter: 1.0 dva

        # according to the website, these need old fashioned 0-255 colors, with a transparency byte [r,g,b,a]

        if self.calibrationpoints == 5:
            calibration['type']='FIVE_POINTS'
        if self.calibrationpoints == 9:
            calibration['type']='NINE_POINTS'

        if 'back' in self.colors.keys():
            calibration['screen_background_color'] = [round((x + 1)*(255/2)) for x in self.colors['back']]+[255]
            calibration['target_attributes']['inner_color'] = [round((x + 1)*(255/2)) for x in self.colors['back']]+[255]
        else:
            calibration['screen_background_color'] = [round((x + 1)*(255/2)) for x in [0.5, 0.5, -1]]+[255] # close enough for most cases?
            calibration['target_attributes']['outer_color'] = [round((x + 1)*(255/2)) for x in [0.5, 0.5, -1]]+[255]

        if 'both' in self.colors.keys():
            calibration['target_attributes']['outer_color'] = [round((x + 1)*(255/2)) for x in self.colors['both']]+[255]
        else:
            calibration['target_attributes']['outer_color'] = [0,0,0,255] # black...




        eyetracker_config['calibration'] = calibration

        devices_config['eyetracker.hw.sr_research.eyelink.EyeTracker'] = eyetracker_config

        # not sure this needs to be stored, but let's just have the info available in the future:
        self.devices_config = devices_config

        # launch a tracker device thing in the iohub:
        # self.io = self.launchHubServer(window = self.psychopyWindow, **devices_config)
        self.io = self.launchHubServer(window = self.__EL_window, **devices_config)

        self.tracker = self.io.getDevice('tracker')

        # this part might not be cool? otoh, we don't need that window any more... and it should not block the main window
        self.__EL_window.close()


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

        [ width, height, sampleRate, offsetX, offsetY ] = self.LiveTrack.GetCaptureConfig()
        self.__LiveTrackConfig = { 'width'      : width,
                                   'height'     : height,
                                   'sampleRate' : sampleRate,
                                   'offsetX'    : offsetX,
                                   'offsetY'    : offsetY      }

    def __DM_initialize(self):
        print('initialize dummy mouse tracker')
        self.__mousetracker = event.Mouse( visible = True,
                                           newPos = None,                    # what does this even do?
                                           win = self.psychopyWindow )
        

    # endregion


    # functions to calibrate each device:
    # region

    def calibrate(self):
        raise Warning("set eyetracker before calibrating it")

    def __EL_calibrate(self):

        self.hideWindow(self.psychopyWindow)
        result = self.tracker.runSetupProcedure()
        print("Calibration returned: ", result)
        self.showWindow(self.psychopyWindow)

        self.__N_calibrations += 1
        self.comment('calibration %d'%(self.__N_calibrations))
        # self.savecalibration() # not sure if this function will just do nothing or if it will not exist for the EyeLink case

    def __LT_calibrate(self):
        # print('calibrate livetrack')

        calTargets = copy.deepcopy(self.__calibrationTargets)

        print(self.calibrationpoints)

        # midTarget = calTargets[0]
        # extTargets = calTargets[1:]

        # np.random.shuffle(extTargets)

        # calTargets = [midTarget].append(extTargets).append(midTarget)

        # ntargets = len(calTargets)

        mididx = list(range(1,len(calTargets)))
        random.shuffle(mididx)
        allidx = [0] + mididx + [0]
        ntargets = len(allidx)


        # configure calibration:
        setupDelay = 1000.0 # time before collecting any samples in ms
        minDur = 300 # min fixation duration in ms
        fixTimeout = 5  # timeout duration in seconds (point is skipped!)
        fixThreshold = 5 # pixel window for all samples within a 'fixation'

        # ntargets = np.shape(self.__calibrationTargets)[0]
        # tgtLocs = self.__calibrationTargets.astype(float) 
        tgtLocs = copy.deepcopy(self.__calibrationTargets)
        tgtLocs = tgtLocs[allidx,:]
        tgtLocs = tgtLocs.astype(float) # make sure locations are floats

        # show calibration on separate video window (not necessary):
        # if self.useVideo:
        #     print('Please align camera')
        #     import LiveTrackGS
        #     LiveTrackGS.VideoInit(0)
        #     result= LiveTrackGS.VideoStart()
        #     time.sleep(5)

        # initialise LiveTrack
        # LiveTrack.Init() # already done

        self.LiveTrack.SetResultsTypeRaw() # stream raw data
        self.LiveTrack.StartTracking() # buffer data to lib
        [ width, height, sampleRate, offsetX, offsetY ] = self.LiveTrack.GetCaptureConfig() # estimate sample rate
        fixDurSamples = round((float(minDur)/1000)*float(sampleRate)) # samples per fixation duration

        self.LiveTrack.SetTracking(self.trackEyes[0], self.trackEyes[1]) # make sure we're only tracking the requires eyes
        # print(self.LiveTrack.GetTracking()) # see what's being tracked

        if self.trackEyes[0]:
            VectXL = [None] * ntargets
            VectYL = [None] * ntargets
            GlintXL = [None] * ntargets
            GlintYL = [None] * ntargets
        if self.trackEyes[1]:
            VectXR = [None] * ntargets
            VectYR = [None] * ntargets
            GlintXR = [None] * ntargets
            GlintYR = [None] * ntargets

        visual.TextStim(self.psychopyWindow,'calibration', height = 1,wrapWidth=30, color = 'black').draw()
        self.psychopyWindow.flip()
        time.sleep(0.25) # is this necessary?

        for target_idx in range(ntargets):
            # plot a circle at the fixation position.
            # self.cal_dot_o.pos = self.calibrationTargets[target_idx,:]
            # self.cal_dot_o.draw()
            # self.cal_dot_i.pos = self.calibrationTargets[target_idx,:]
            # self.cal_dot_i.draw()

            targetpos = tgtLocs[target_idx]

            self.target.pos = targetpos
            self.target.draw()

            self.psychopyWindow.flip()

            # This flag will be set to true when a valid fixation has been acquired
            gotFixLeft = 0  
            gotFixRight = 0
            
            t0 = time.time() # reset fixation timer 
        
            # Loop until fixation data has been aquired for this dot (or timed out) 
            while 1:
                d = self.LiveTrack.GetBufferedEyePositions(0,fixDurSamples,0)

                if self.trackEyes[0]:

                    VectX = self.LiveTrack.GetFieldAsList(d,'VectX')
                    VectY = self.LiveTrack.GetFieldAsList(d,'VectY')
                    GlintX = self.LiveTrack.GetFieldAsList(d,'GlintX')
                    GlintY = self.LiveTrack.GetFieldAsList(d,'GlintY')
                    Tracked = self.LiveTrack.GetFieldAsList(d,'Tracked')

                    # Calculate the maximum difference in the pupil-to-glint 
                    # vectors for the samples in the buffer, for left eye
                    pgDistL = max([max(VectX)-min(VectX),max(VectY)-min(VectY)])

                    # Check if the maximum vector difference is within the defined
                    # limit for a fixation (fixWindow) and all samples ajsone tracked, and
                    # the time to wait for fixations (waitTimeForFix) has passed, for
                    # the left eye
                    if pgDistL<=fixThreshold and np.all(Tracked) and (time.time()-t0)>setupDelay/1000:
                        # Check if there are enough samples in the buffer for the
                        # defined duration (fixDurSamples)
                        if len(d)>=fixDurSamples and gotFixLeft==0:
                            # save the data for this fixation
                            VectXL[target_idx] = np.median(VectX)
                            VectYL[target_idx] = np.median(VectY)
                            GlintXL[target_idx] = np.median(GlintX)
                            GlintYL[target_idx] = np.median(GlintY)
                            print('Fixation #',str(target_idx+1),str(targetpos),': Found valid fixation for left eye')
                            gotFixLeft = 1 # good fixation aquired
                
                if self.trackEyes[1]:
                    VectXRight = self.LiveTrack.GetFieldAsList(d,'VectXRight')
                    VectYRight = self.LiveTrack.GetFieldAsList(d,'VectYRight')
                    GlintXRight = self.LiveTrack.GetFieldAsList(d,'GlintXRight')
                    GlintYRight = self.LiveTrack.GetFieldAsList(d,'GlintYRight')
                    TrackedRight = self.LiveTrack.GetFieldAsList(d,'TrackedRight')
                
                    # and for the right eye
                    pgDistR = max([max(VectXRight)-min(VectXRight),max(VectYRight)-min(VectYRight)])


                    # and for the right eye
                    if pgDistR<=fixThreshold and np.all(TrackedRight) and (time.time()-t0)>setupDelay/1000:
                        # Check if there are enough samples in the buffer for the
                        # defined duration (fixDurSamples)
                        if  len(d)>=fixDurSamples and gotFixRight==0:
                            # save the data for this fixation
                            VectXR[target_idx] = np.median(VectXRight)
                            VectYR[target_idx] = np.median(VectYRight)
                            GlintXR[target_idx] = np.median(GlintXRight)
                            GlintYR[target_idx] = np.median(GlintYRight)
                            print('Fixation #',str(target_idx+1),str(targetpos),': Found valid fixation for right eye')
                            gotFixRight = 1 # good fixation aquired
                

                if (time.time()-t0)>fixTimeout:
                    if not gotFixLeft and self.trackEyes[0]>0:
                        print('Fixation #',str(target_idx+1),str(targetpos),': Did not get fixation for left eye (timeout)')
                    if not gotFixRight and self.trackEyes[1]>0:
                        print('Fixation #',str(target_idx+1),str(targetpos),': Did not get fixation for right eye (timeout)')
                    break # fixation timed out

                
                # Exit if all eyes that are enabled have got a fixation
                if (gotFixLeft or self.trackEyes[0]==False) and (gotFixRight or self.trackEyes[1]==False):
                    self.psychopyWindow.flip()
                    break

        # Stop buffering data to the library
        ######################################################### NOT SURE ABOUT THIS:

        self.LiveTrack.StopTracking()

        # Clear the data in the buffer
        self.LiveTrack.ClearDataBuffer()


        viewDist = self.psychopyWindow.monitor.getDistance()

        # %% remove failed fixations from data

        if self.trackEyes[0]:
            # left eye
            failedFixL = []
            for i in range(0,len(VectXL)):
                if VectXL[i] is None:
                    failedFixL.append(i)
            
            # %% remove failed fixations from data
            VectXL = np.delete(VectXL, failedFixL).tolist()
            VectYL = np.delete(VectYL, failedFixL).tolist()
            GlintXL = np.delete(GlintXL, failedFixL).tolist()
            GlintYL = np.delete(GlintYL, failedFixL).tolist()
            tgtLocsXL = np.delete(tgtLocs[:,0], failedFixL).tolist()
            tgtLocsYL = np.delete(tgtLocs[:,1], failedFixL).tolist()

            # %% send fixation data to LiveTrack to calibrate
            calErrL = self.LiveTrack.CalibrateDevice(0, len(tgtLocsXL), tgtLocsXL, tgtLocsYL, VectXL, VectYL, viewDist, np.median(GlintXL), np.median(GlintYL))
            print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrL)/len(tgtLocsXL))), 'errors in dva')


        if self.trackEyes[1]:
            # right eye
            failedFixR = []
            for i in range(0,len(VectXR)):
                if VectXR[i] is None:
                    failedFixR.append(i)

            # %% remove failed fixations from data
            VectXR = np.delete(VectXR, failedFixR).tolist()
            VectYR = np.delete(VectYR, failedFixR).tolist()
            GlintXR = np.delete(GlintXR, failedFixR).tolist()
            GlintYR = np.delete(GlintYR, failedFixR).tolist()
            tgtLocsXR = np.delete(tgtLocs[:,0], failedFixR).tolist()
            tgtLocsYR = np.delete(tgtLocs[:,1], failedFixR).tolist()
            
            calErrR = self.LiveTrack.CalibrateDevice(1, len(tgtLocsXR), tgtLocsXR, tgtLocsYR, VectXR, VectYR, viewDist, np.median(GlintXR), np.median(GlintYR))
            print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrR)/len(tgtLocsXR))), 'errors in dva')
        

        # %% plot the estimated fixation locations for the calibration
        #if trackLeftEye:
        #    [gazeXL, gazeYL] = LiveTrack.CalcGaze(0, len(tgtLocsXL), VectXL, VectYL)
        #
        #if trackRightEye:
        #    [gazeXR, gazeYR] = LiveTrack.CalcGaze(1, len(tgtLocsXR), VectXR, VectYR)
        # errors are added?
        # gazeXL = [x+10 for x in tgtLocsXL]
        # gazeYL = [x+10 for x in tgtLocsYL]
        # gazeXR = [x-10 for x in tgtLocsXR]
        # gazeYR = [x-10 for x in tgtLocsYR]
        
        # if useVideo:
        #     self.LiveTrackGS.VideoStop()

        self.LiveTrack.SetResultsTypeCalibrated()

        self.__N_calibrations += 1
        self.comment('calibration %d'%(self.__N_calibrations))
        if self.storefiles:
            self.savecalibration()

    def __DM_calibrate(self):
        self.__N_calibrations += 1
        self.comment('calibration %d'%(self.__N_calibrations))
    
    # endregion

    def savecalibration(self):
        raise Warning("default function: tracker not set")

    def __EL_savecalibration(self):
        print('not saving calibrations for the EyeLink')
        # not sure if it's worth pulling out the calibration info...

    def __LT_savecalibration(self):

        # collect calibration info in a dictionary:
        calibrations = {}
        if self.trackEyes[0]:
            calibrations['left']  = self.LiveTrack.GetCalibration(eye=0)
        if self.trackEyes[1]:
            calibrations['right'] = self.LiveTrack.GetCalibration(eye=1)

        # write calibration info to a json file:
        filename = '%s/calibration_%s.json'%(self.filefolder, self.__N_calibrations)
        out_file = open(filename, "w")
        json.dump( calibrations,
                   fp=out_file,
                   indent=4)
        out_file.close()

    def __DM_savecalibration(self):
        print('not saving 1:1 mouse calibration')

    
    # endregion


    # function to open new raw data file
    # region

    def openfile(self, filename=None):
        raise Warning('default function: tracker not set')
        # has to do:
        # - make filename if not given
        # - if filename has a path: strip it
        # - make sure te filename is formatted correctly: extension is EDF (eyelink) or CSV (livetrack)
        # - check if currently, a file is open
        # - if so: close it (and print a statement!)
        # - open the new file
        # - set self.__fileOpen True (do we need to store the current filename?)
        # - increment self.__N_rawdatafiles by +1


    def __EL_openfile(self, filename=None):
        # print('placeholder function: openfile EyeLink')
        return(None) # done at the level of the whole session

        # if self.__fileOpen:
        #     self.closefile()
        #     print('note: closed open file before opening a new file')

        # filename = saneFilename(filename, ext='.edf')

        # # # # # # # # #
        # now what?

        # https://psychopy.org/api/iohub/device/eyetracker_interface/SR_Research_Implementation_Notes.html
        # it seems to be this option in the config dictionary:
        # default_native_data_file_name: et_data



    def __LT_openfile(self):
        
        # maybe this should also be done at the level of the whole session?
        # yes!

        if self.__fileOpen:
            self.closefile()
            print('note: closed open file before opening a new file')

        # filename = self.saneFilename(self.filename, ext='.csv')


        print(os.path.join(self.filefolder,self.filename)+'.csv')
        self.LiveTrack.SetDataFilename(os.path.join(self.filefolder,self.filename)+'.csv')

        self.__fileOpen = True
        self.__N_rawdatafiles += 1


    def __DM_openfile(self, filename=None):
        print('not opening raw data file for dummy mouse tracker')


    def saneFilename(self, filename, ext):

        if filename == None:
            filename = 'raw_%d%s'%(self.__N_rawdatafiles+1, ext)
        else:
            if isinstance(filename, str):
                if len(filename) > 0:
                    if not(os.path.isfile(filename)):
                        file_path, file_ext = os.path.splitext(filename)
                        if not(file_ext in [ext,ext.upper()]):
                            file_ext = '.csv'
                            filename = file_path + file_ext
                            print("changed file extention to '.csv'")
                        if len(os.path.dirname(filename)) > 0:
                            filename = os.path.basename(filename)
                            print('storing in designated folder: path removed from filename')
                    else:
                        raise Warning('file already exists')
                else:
                    raise Warning('filename should have non-zero length')
            else:
                raise Warning('filename should be a string')

        return(filename)

    # endregion


    # function to start collecting raw data
    # region
    def startcollecting(self):
        raise Warning("default function: tracker not set")

    def __EL_startcollecting(self):
        self.tracker.setRecordingState(True)

    def __LT_startcollecting(self):
        self.LiveTrack.StartTracking()

    def __DM_startcollecting(self):
        print('not implemented: startcollecting dummy mouse data')

    # endregion


    # function to stop collecting raw data
    # region

    def stopcollecting(self):
        raise Warning("default function: tracker not set")

    def __EL_stopcollecting(self):
        self.tracker.setRecordingState(False)


    def __LT_stopcollecting(self):
        self.LiveTrack.StopTracking()

    def __DM_stopcollecting(self):
        print('not implemented: stopcollecting dummy mouse data')


    # endregion

    # function to close existing raw data file
    # region

    def closefile(self):
        raise Warning("default function: tracker not set")

    def __EL_closefile(self):
        # send command to EyeLink to close the EDF with raw data
        # if self.__fileOpen:
        #     if len(self.__EL_currentfile) == 0:
        #         print('no file to close')
        #     else:
        #         # these two lines from Clement:
        #         self.tracker.setRecordingState(False)
        #         self.io.clearEvents()

        #         # extra bookkeeping:
        #         self.__EL_downloadFiles.append(self.__EL_currentfile)
        #         self.__EL_currentfile = ''
        #         self.__fileOpen = False
        # else:
        #     print('no file to close')

        return(None)
            

    def __LT_closefile(self):
        if self.__fileOpen:
            self.LiveTrack.CloseDataFile()
            self.__fileOpen = False
        else:
            print('no file to close, moving on')

    def __DM_closefile(self):
        if self.__fileOpen:
            print('open file for dummy mouse? this should not happen...')
            self.__fileOpen = False
        else:
            print('no file to close, moving on')

    # endregion


    # the following functions are used during the experiment:

    # get the last sample from the specified tracker:
    # region

    def lastsample(self):
        raise Warning("default function: tracker not set")

    def __EL_lastsample(self):
        # print('not implemented: getting last eyelink sample')
        # probably needs to be converted to dva... using built-in psychopy functions?
        # do we need to account for the origin/offset?
        o = self.__EL_offset # subtract this from X,Y coordinates to get coordinates with (0,0) at the center of the screen
        # do we need to scale from pixels to degrees? (in this case, this is a flat multiplication factor, more than good enough around fixation)
        p = self.__EL_p2df # multiply pixel values by this to get degrees...

        # for now this uses IOhub gaze position:
        # the average of the left and right gaze position
        # this could be expanded in the future
        gpos = self.tracker.getLastGazePosition()
        # gpos is either None (no valid tracking) or a tuple or list of 2 numbers: X/Y coordinates
        if isinstance(gpos, (tuple, list)):
            # data = (np.array(gpos) - o) * p # is the origin already the middle of the screen? would be a psychopy thing to do
            data = (np.array(gpos)) * p
        else:
            data = np.array([np.NaN, np.NaN])

        sample = {}

        if self.samplemode == 'both':
            sample['left'] = data
            sample['right'] = data
        if self.samplemode == 'left':
            sample['left'] = data
        if self.samplemode == 'right':
            sample['right'] = data
        if self.samplemode == 'average':
            sample['average'] = data

        return(sample)


    def __LT_lastsample(self):
        # data = LiveTrack.GetBufferedEyePositions(0,fixDurSamples,0) # this would get the last x samples, given by the second argument
        data = self.LiveTrack.GetLastResult() # gets only the very last sample

        # this needs to be formatted in some standard way that is the same for all eye-tracker devices
        sample = {}
        if self.samplemode in ['both','left','average']:
            if self.trackEyes[0]:
                if data.Tracked:
                    sample['left'] = np.array([data.GazeX, data.GazeY])
                else:
                    sample['left'] = np.array([np.NaN, np.NaN])
        if self.samplemode in ['both','right','average']:
            if self.trackEyes[1]:
                if data.TrackedRight:
                    sample['right'] = np.array([data.GazeXRight, data.GazeYRight])
                else:
                    sample['right'] = np.array([np.NaN, np.NaN])

        if self.samplemode == 'average':
            X = []
            Y = []
            # skip NAN values?
            if data.Tracked:
                X.append(sample['left'][0])
                Y.append(sample['left'][1])
            if data.TrackedRight:
                X.append(sample['right'][0])
                Y.append(sample['right'][1])
            if (any([data.Tracked, data.TrackedRight])):
                sample['average'] = np.array([np.mean(X), np.mean(Y)])

        return(sample)

    def __DM_lastsample(self):
        # print('not implemented: getting last dummy mouse sample')
        data = np.array(self.__mousetracker.getPos())

        sample = {}

        if self.samplemode == 'both':
            sample['left'] = data
            sample['right'] = data
        if self.samplemode == 'left':
            sample['left'] = data
        if self.samplemode == 'right':
            sample['right'] = data
        if self.samplemode == 'average':
            sample['average'] = data

        return(sample)
        # this needs to be formatted in some standard way that is the same for all eye-tracker devices
        # copied to each eye?


    # endregion


    def gazeInFixationWindow(self):

        sample = self.lastsample()
        check_samples = self.getSamplesToCheck()
        
        for cs in check_samples: # skipping irrelevant sample types
            if cs in sample.keys():
                if any(np.isnan(sample[cs])):
                    return(False) # return False if there is a nan value
                d = np.sqrt(np.sum(np.array(sample[cs])**2))
                if d > self.fixationWindow:
                    return(False) # return false if the distance from fixation is larger than 2 (or whatever the fixation window is)
            else:
                return(False) # return false if any of the samples that need to be checked are not in the data

        return(True) # should only get here if all samples exist, are not nans, and are within the fixation window



    def getSamplesToCheck(self):

        return( {'both':['left','right'],
                 'left':['left'],
                 'right':['right'],
                 'average':['average']}[self.samplemode] )

    def waitForFixation(self, minFixDur=None, fixTimeout=None):

        if minFixDur == None:
            minFixDur = self.minFixDur
        if fixTimeout == None:
            fixTimeout = self.fixTimeout

        self.target.pos = [0,0]

        # most the initially set values should be used, but we do 1 sanity check here:
        # if the initially set values are used, this should already be true:
        if fixTimeout < minFixDur:
            raise Warning("fixation timeout should be longer than minimum fixation duration")

        starttime = time.time()
        timeout = starttime + fixTimeout
        now = starttime

        fixationStart = None

        while now < timeout:

            self.target.draw()
            self.psychopyWindow.flip()

            now = time.time()

            fixated = self.gazeInFixationWindow()

            if fixated:
                if fixationStart == None:
                    fixationStart = now
                else:
                    if (now - fixationStart) >= minFixDur:
                        return True
            else:
                fixationStart = None
        
        return False





    # insert a comment into the raw data file storing tracker data:
    # region
    def comment(self, comment):
        raise Warning("default function: tracker not set")

    def __EL_comment(self, comment):
        # based on this thread:
        # https://discourse.psychopy.org/t/eyelink-1000-output-file-doesnt-have-trial-or-event-information/25699
        if self.__fileOpen:
            self.tracker.sendMessage(comment)
        # do we need to wait for some time?
        # does this prepend MSG before the message?

    def __LT_comment(self, comment):

        if self.__fileOpen:
            self.LiveTrack.SetDataComment(comment)
            time.sleep(1.5/self.__LiveTrackConfig['sampleRate'])
        # the experiment sleeps for 1.5 eye-tracker samples
        # this ensures actually storing the comment
        # and doesn't get overwritten by the next comment... at the same sample (shouldn't send comments that quickly?)
        # and we might skip 1 sample, but that will be less than 1 frame


    def __DM_comment(self, comment):
        print('DM comment: %s'%(comment))
        # also: probably won't be implemented, because there is no such file?
        # this would require starting a different thread or so
        # that takes all the mouse coordinates, at some sampling rate, separately from the experiment, and... 
        # no... doesn't sound like a plan to me


    # endregion





    # functions to close the eye-tracker
    # region

    def shutdown(self):
        raise Warning("default function: tracker not set")

    def __EL_shutdown(self):
        self.stopcollecting()
        self.closefile()
        self.tracker.setConnectionState(False)
        self.io.quit()
        if os.path.isfile('et_data.EDF'):
            os.remove('et_data.EDF')

    def __LT_shutdown(self):
        self.stopcollecting()
        self.closefile()
        self.LiveTrack.Close()

    def __DM_shutdown(self):
        print('[dummy mouse shutdown called]')
        # no need for any shutdown action, it seems:
        # there are no files, and connections to close

    # endregion

    # this runs shutdown on garbage collection
    # which could be much later then expected
    # it's to make sure it gets doen at some point
    def __del__(self):
        self.shutdown()


    def __createTargetStim(self):
        
        # should these be accessible / changeble by the user?
        fixDotInDeg  = 0.2 # inner circle
        fixDotOutDeg = 1.0
        
        self.target = visual.TargetStim(self.psychopyWindow, 
                                        name='fixTarget',
                                        radius=fixDotOutDeg/2, 
                                        innerRadius=fixDotInDeg/2, 
                                        fillColor=[-1,-1,-1], 
                                        innerFillColor=[1,1,1], 
                                        lineWidth=0, 
                                        innerLineWidth=0, 
                                        borderColor=None, 
                                        innerBorderColor=None,
                                        units='deg')



def localizeSetup( trackEyes, filefolder, filename, location=None, glasses='RG', colors=None, task=None, ID=None ):
    
    # sanity checks on trackEyes, filefolder and filename are done by the eyetracker object

    # sanity check on location argument
    if location == None:
        raise Warning("set location to a string: Glasgow or Toronto")
    if isinstance(location, str):
        if location in ['Toronto', 'toronto', 'tor', 'TOR', 't', 'T', 'YYZ']:
            location = 'toronto'
        if location in ['Glasgow', 'glasgow', 'gla', 'GLA', 'g', 'G', 'EGPF']:
            location = 'glasgow'
    else:
        raise Warning("set location to a string: Glasgow or Toronto")



    # RED/GREEN COLORS

    if colors == None:
        colors = {}

    # sanity check on glasses argument, and picking back-ground color
    if isinstance(glasses, str):
        if glasses in ['RG', 'RB']:
            if glasses == 'RG':
                if location == 'glasgow':
                    colors['back']   = [ 0.55,  0.45, -1.00] 
                    colors['red']    = [ 0.55, -1.00, -1.00]
                    colors['blue']   = [-1.00,  0.45, -1.00]
                if location == 'toronto':
                    colors['back']   = [ 0.5,   0.5,  -1.0 ]
                    colors['red']    = [ 0.5,  -1.0,  -1.0 ]
                    colors['blue']   = [-1.0,   0.5,  -1.0 ]
            if glasses == 'RB':
                # this should no longer be used:
                print('are you sure about using RED/BLUE glasses?')
                colors['back']   = [ 0.5, -1.0,  0.5]
                colors['red']    = [ 0.5, -1.0, -1.0]
                colors['blue']   = [-1.0, -1.0,  0.5] 
        else:
            raise Warning('glasses should be RG (default) or RB')
    else:
        raise Warning('glasses should be a string')

    # CALIBRATED COLORS:

    # for blind spot mapping, task == None, but it still needs the calibrated colors...
    # handle this in the function?
    colors = getColors(colors=colors, task=task, ID=ID)


    # WINDOW OBJECT

    if location == 'glasgow':
        # not a calibrated monitor?
        gammaGrid = np.array([ [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ],
                               [  0., 1.0, 1.0, np.nan, np.nan, np.nan  ]  ], dtype=np.float32)

        resolution = [1920, 1080] # in pixels
        size       = [60, 33.75] # in cm
        distance   = 57 # in cm
        screen     = 1 # index on the system: 0 = first monitor, 1 = second monitor, and so on

        tracker = 'eyelink'


    if location == 'toronto':
        # color calibrated monitor:
        gammaGrid = np.array([ [  0., 135.44739,  2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,  27.722954, 2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,  97.999275, 2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,   9.235623, 2.4203537, np.nan, np.nan, np.nan  ]  ], dtype=np.float32)

        resolution = [1920, 1080] # in pixels
        size       = [59.8, 33.6] # in cm
        distance   = 50 # in cm
        screen     = 0  # index on the system: 0 = first monitor, 1 = second monitor, and so on

        tracker = 'livetrack'

    mymonitor = monitors.Monitor(name='temp',
                                 distance=distance,
                                 width=size[0])
    if location == 'toronto':
        mymonitor.setGammaGrid(gammaGrid)
    mymonitor.setSizePix(resolution)



    #win = visual.Window([1000, 500], allowGUI=True, monitor='ccni', units='deg', fullscr=True, color = back_col, colorSpace = 'rgb')
    win = visual.Window(resolution, monitor=mymonitor, allowGUI=True, units='deg', fullscr=True, color=colors['back'], colorSpace = 'rgb', screen=screen)
            # size = [34.5, 19.5]filefolder,

    fixation = visual.ShapeStim(win, 
                                vertices = ((0, -1), (0, 1), (0,0), (-1, 0), (1, 0)), 
                                lineWidth = 5, 
                                units = 'deg', 
                                size = (1, 1), # might be too small?
                                closeShape = False, 
                                lineColor = [-0.5, -0.5, -1.0]) # close to col_both?

    if 'both' in colors.keys():
        fixation.lineColor = colors['both']


    if not any(trackEyes):
        tracker = 'mouse'
        trackEyes = [True, False]

    print(filefolder)

    ET = EyeTracker(tracker           = tracker,
                    trackEyes         = trackEyes,
                    fixationWindow    = 2.0,
                    minFixDur         = 0.2,
                    fixTimeout        = 3.0,
                    psychopyWindow    = win,
                    filefolder        = filefolder,
                    filename          = filename,
                    samplemode        = 'average',
                    calibrationpoints = 5,
                    colors            = colors )


    fcols = [[-1,-1,-1],[1,1,1]]
    if 'both' in colors.keys():
        fcols[0] = colors['both']
    if 'back' in colors.keys():
        fcols[1] = colors['back']

    fusion = {'hi': fusionStim(win    = win,
                               pos    = [0,7],
                               colors = fcols),
              'lo': fusionStim(win    = win,
                               pos    = [0,-7],
                               colors = fcols)}

    # color calibration doesn't use any of this (except the window object?)
    # for either calibration task, the task should not be set
    # which returns an empty dictionary
    blindspotmarkers = makeBlindSpotMarkers(win=win, task=task, ID=ID, colors=colors)

    return( {'win'              : win,
             'tracker'          : ET,
             'colors'           : colors,
             'fusion'           : fusion,
             'fixation'         : fixation,
             'blindspotmarkers' : blindspotmarkers } )

def getColors(colors, task, ID):

    if task == None:
        return(colors)

    if ID == None:
        return(colors)

    ## colour (eye) parameters
    all_files = glob('../data/' + task + '/color/' + ID + '_col_cal*.txt')
    if len(all_files) == 0:
        # no color calibration done, skip
        return(colors)
    col_file = open(all_files[-1],'r')
    col_param = col_file.read().replace('\t','\n').split('\n')
    col_file.close()

    # let's flip this depending on the task run, in each of the experiments?
    # col_ipsi = eval(col_param[3]) if hemifield == 'left' else eval(col_param[5]) # left or right
    # col_cont = eval(col_param[5]) if hemifield == 'left' else eval(col_param[3]) # right or left

    # so use the left / right things for now
    colors['left']  = col_param[3]
    colors['right'] = col_param[5]

    # both should be defined in 1 way... up for grabs how, afaic
    # colors['both']  = [-0.7, -0.7, -0.7] # from 2nd FBE version of the distance task
    colors['both']  = [eval(col_param[3])[1], eval(col_param[5])[0], -1]

    return(colors)

    

def makeBlindSpotMarkers(win, task, ID, colors):

    if task == None:
        return({})

    if ID == None:
        return({})

    main_path = '../data/' + task + '/'
    
    ## blindspot parameters
    bs_file = open(glob(main_path + 'mapping/' + ID + '_LH_blindspot*.txt')[-1], 'r')
    bs_param = bs_file.read().replace('\t','\n').split('\n')
    bs_file.close()
    spot_left_cart = eval(bs_param[1])
    spot_left = cart2pol(spot_left_cart[0], spot_left_cart[1])
    spot_left_size = eval(bs_param[3])

    bs_file = open(glob(main_path + 'mapping/' + ID + '_RH_blindspot*.txt')[-1],'r')
    bs_param = bs_file.read().replace('\t','\n').split('\n')
    bs_file.close()
    spot_righ_cart = eval(bs_param[1])
    spot_righ = cart2pol(spot_righ_cart[0], spot_righ_cart[1])
    spot_righ_size = eval(bs_param[3])


    blindspotmarkers = {}
    
    for hemifield in ['left','right']:

        if hemifield == 'left':
            spot_cart = spot_left_cart
            spot      = spot_left
            spot_size = spot_left_size
        else:
            spot_cart = spot_righ_cart
            spot      = spot_righ
            spot_size = spot_righ_size

        tar =  spot_size[0] + 2 + 2

        # size of blind spot + 2 (dot width, padding)
        if hemifield == 'left' and spot_cart[1] < 0:
            ang_up = (cart2pol(spot_cart[0], spot_cart[1] - spot_size[1])[0] - spot[0]) + 2
        else:
            ang_up = (cart2pol(spot_cart[0], spot_cart[1] + spot_size[1])[0] - spot[0]) + 2

        blindspot = visual.Circle(win, radius = .5, pos = [7,0], units = 'deg', fillColor=colors[hemifield], lineColor = None)
        blindspot.pos = spot_cart
        blindspot.size = spot_size
        # blindspot.autoDraw = True
        # set autodraw only on the one used in the task

        blindspotmarkers[hemifield] = blindspot

    return(blindspotmarkers)



class fusionStim:

    def __init__(self, 
                 win, 
                 pos     = [0,0],
                 colors  = [[-1,-1,-1],[1,1,1]],
                 rows    = 15,
                 columns = 3,
                 square  = 0.5,
                 units   = 'deg'):

        self.win     = win
        self.pos     = pos
        self.colors  = colors
        self.rows    = rows
        self.columns = columns
        self.square  = square
        self.units   = units

        self.resetProperties()

    def resetProperties(self):
        self.nElements = (self.columns*2 + 1) * self.rows

        self.setColorArray()
        self.setPositions()
        self.createElementArray()

    def setColorArray(self):
        self.colorArray = (self.colors * int(np.ceil(((self.columns*2 + 1) * self.rows)/len(self.colors))))
        random.shuffle(self.colorArray)
        self.colorArray = self.colorArray[:self.nElements]

    def setPositions(self):
        self.xys = [[(i * self.square)+self.pos[0], ((j-((self.rows-1)/2))*self.square)+self.pos[1]] for i in range(-self.columns, self.columns + 1) for j in range(self.rows)]

    def createElementArray(self):
        self.elementArray = visual.ElementArrayStim( win         = self.win, 
                                                     nElements   = self.nElements,
                                                     sizes       = self.square, 
                                                     xys         = self.xys, 
                                                     colors      = self.colorArray, 
                                                     units       = self.units, 
                                                     elementMask = 'none', 
                                                     sfs         = 0)

    def draw(self):
        self.elementArray.draw()
