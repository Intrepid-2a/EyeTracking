import sys
import warnings
import numbers
import numpy as np
import time
import math

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

        # things below this comment are still up for change... depends a bit on how the EyeLink does things

        # maybe these should be a property that has a function to set it?
        self.calibrationTargets = np.array([[0,0],   [-3,0],[0,3],[3,0],[0,-3],     [6,6],[6,-6],[-6,6],[-6,-6]])

        # the innner and outer calibration dot size can be changed later on, but the stimuli will have already been made...
        self.fixDotInDeg  = 0.2 # inner circle
        self.fixDotOutDeg = 1.0
        self.cal_dot_o = visual.Circle(self.psychopyWindow,units='deg',radius=self.fixDotOutDeg/2,fillColor=[-1,-1,-1],lineWidth=0,pos=[0,0]) # outer circle
        self.cal_dot_i = visual.Circle(self.psychopyWindow,units='deg',radius=self.fixDotInDeg/2,fillColor=[ 1, 1, 1],lineWidth=0,pos=[0,0]) # inner circle



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
            self.psychopyWindow = psychopyWindow
        else:
            raise Warning("psychopyWindow must by a psychopy Window")

    def setupEyeLink(self):
        
        # python library to interface with EyeLink:
        import pylink
        self.pylink = pylink

        # psychopy iohub stuff to make things a bit easier:
        from psychopy.iohub.client import launchHubServer
        self.launchHubServer = launchHubServer
        from psychopy.iohub.util import hideWindow, showWindow
        self.hideWindow = hideWindow
        self.showWindow = showWindow




        # remap functions:
        self.initialize = self.__EL_initialize
        # self.calibrate  = self.__EL_calibrate

        self.lastsample = self.__EL_lastsample

        self.startcollecting = self.__EL_startcollecting
        self.stopcollecting = self.__EL_stopcollecting

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

        self.lastsample = self.__LT_lastsample

        self.startcollecting = self.__LT_startcollecting
        self.stopcollecting = self.__LT_stopcollecting

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

        self.lastsample = self.__DM_lastsample

        self.startcollecting = self.__DM_startcollecting
        self.stopcollecting = self.__DM_stopcollecting

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
        print('initialize EyeLink')

        track_eyes = None

        if all(self.trackEyes):
            track_eyes = 'BOTH'
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
        eyetracker_config = dict(name='tracker')
        eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
        eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, track_eyes=track_eyes)
        eyetracker_config['calibration'] = dict(screen_background_color=(0,0,0))
        devices_config['eyetracker.hw.sr_research.eyelink.EyeTracker'] = eyetracker_config

        # not sure this needs to be stored, but let's just have the info available in the future:
        self.devices_config = devices_config

        # launch a tracker device thing in the iohub:
        self.io = self.launchHubServer(window = self.psychopyWindow, **devices_config)
        self.tracker = self.io.getDevice('tracker')



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
        print('initialize dummy mouse tracker')
        self.__mousetracker = event.Mouse( visible = True,
                                           newPos = None,
                                           win = self.psychopyWindow )
        

    # endregion


    # functions to calibrate each device:
    # region

    def calibrate(self):
        raise Warning("set eyetracker before calibrating it")

    def __EL_calibrate(self):
        print('calibrate EyeLink')

    def __LT_calibrate(self):
        print('calibrate livetrack')
        np.random.shuffle(self.calibrationTargets)

        # configure calibration:
        setupDelay = 1000.0 # time before collecting any samples in ms
        minDur = 300 # min fixation duration in ms
        fixTimeout = 5  # timeout duration in seconds (point is skipped!)
        fixThreshold = 5 # pixel window for all samples within a 'fixation'

        ntargets = np.shape(self.calibrationTargets)[0]
        tgtLocs = self.calibrationTargets.astype(float) # make sure locations are floats

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
        # time.sleep(0.5) # is this necessary?

        for target_idx in range(ntargets):
            # plot a circle at the fixation position.
            self.cal_dot_o.pos = self.calibrationTargets[target_idx,:]
            self.cal_dot_o.draw()
            self.cal_dot_i.pos = self.calibrationTargets[target_idx,:]
            self.cal_dot_i.draw()
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
                    # limit for a fixation (fixWindow) and all samples are tracked, and
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
                            print('Fixation #',str(target_idx+1),str(self.calibrationTargets[target_idx,:]),': Found valid fixation for left eye')
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
                            print('Fixation #',str(target_idx+1),str(self.calibrationTargets[target_idx,:]),': Found valid fixation for right eye')
                            gotFixRight = 1 # good fixation aquired
                

                if (time.time()-t0)>fixTimeout:
                    if not gotFixLeft and self.trackEyes[0]>0:
                        print('Fixation #',str(target_idx+1),str(self.calibrationTargets[target_idx,:]),': Did not get fixation for left eye (timeout)')
                    if not gotFixRight and self.trackEyes[1]>0:
                        print('Fixation #',str(target_idx+1),str(self.calibrationTargets[target_idx,:]),': Did not get fixation for right eye (timeout)')
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

    def __DM_calibrate(self):
        print('dummy mouse calibration')
        print('(does nothing)')

    
    # endregion

    # functions to save calibration
    # region

    def savecalibration(self):
        raise Warning("default function: tracker not set")

    def __EL_savecalibration(self):
        print('can we even save the EyeLink calibration?')

    def __LT_savecalibration(self):
        print('this needs a filename, probably... not sure where that would come from')

    def __DM_savecalibration(self):
        print('not saving mouse calibration, it is 1:1')

    
    # endregion


    # function to start collecting raw data
    # region
    def startcollecting(self):
        raise Warning("default function: tracker not set")

    def __EL_startcollecting(self):
        print('not implemented: startcollecting EyeLink')

    def __LT_startcollecting(self):
        print('not implemented: startcollecting LiveTrack')

    def __DM_startcollecting(self):
        print('not implemented: startcollecting dummy mouse')

    # endregion


    # function to stop collecting raw data
    # region

    def stopcollecting(self):
        raise Warning("default function: tracker not set")

    def __EL_stopcollecting(self):
        print('not implemented: stopcollecting EyeLink')

    def __LT_stopcollecting(self):
        print('not implemented: stopcollecting LiveTrack')

    def __DM_stopcollecting(self):
        print('not implemented: stopcollecting dummy mouse')


    # endregion




    # the following functions are used during the experiment:

    # get the last sample from the specified tracker:
    # region

    def lastsample(self):
        raise Warning("default function: tracker not set")

    def __EL_lastsample(self):
        print('not implemented: getting last eyelink sample')
        # probably needs to be converted to dva... using built-in psychopy functions
        

    def __LT_lastsample(self):
        print('not implemented: getting last livetrack sample')
        data = self.LiveTrack.GetLastResult()
        # this needs to be formatted in some standard way that is the same for all eye-tracker devices

    def __DM_lastsample(self):
        print('not implemented: getting last dummy mouse sample')
        data = self.__mousetracker.getPos()
        # this needs to be formatted in some standard way that is the same for all eye-tracker devices
        # copied to each eye?


    # endregion


    # insert a comment into the raw data file storing tracker data:
    # region
    def comment(self, comment):
        raise Warning("default function: tracker not set")

    def __EL_comment(self, comment):
        print('not implemented: storing a comment in the raw eyelink data file')
        # check if there is a current file where data is actively being recorded
        # format as a message that the EyeLink can handle?
        # - replace spaces with underscores?
        # - maximum length?

    def __LT_comment(self, comment):
        print('not implemented: storing a comment in the raw livetrack data file')
        # check if there is a current file where data is actively being recorded

    def __DM_comment(self, comment):
        print('not implemented: storing a comment in the raw dummy mouse data file')
        # also: probably won't be implemented, because there is no such file?
        # this would require starting a different thread or so, that takes all the mouse coordinates and... no doesn't sound like a plan to me


    # endregion





    # functions to close the eye-tracker
    # region

    def shutdown(self):
        raise Warning("default function: tracker not set")

    def __EL_shutdown(self):
        print('not implemented yet: EyeLink shutdown')

    def __LT_shutdown(self):
        print('not implemented yet: LiveTrack shutdown')

    def __DM_shutdown(self):
        print('not implemented yet: dummy mouse shutdown')

    # endregion


















