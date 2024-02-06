# Intrepid 2a EyeTracking

An object that implements some eye tracking functionality for the EyeLink, the LiveTrack Lightning, as well as a debug mode using the mouse.

The object will have a few properties:
- which eye-tracker mode to use
- toggle for tracking each eye
- window for accepting a fixation

It needs to be associated with a PsychoPy window as well.

These properties can be set when initializing the object, but there should be methods to change them as well:

`setEyetracker()`
**arguments:**
- tracker: _string_: ['eyelink', 'livetrack', 'mouse']

`trackEyes()`
**arguments:**
- trackEyes: _list of 2 booleans_: left and right eye

`setFixationWindow()`
**arguments:**
- fixationWindow: _number_ (float, int, ...) setting the maximum deviation from the fixation point in the units of the psychopy window

`setPsychopyWindow()`
**arguments:**
- psychopyWindow: _psychopy window object_ assumes that the psychopy window has the unit set to degrees



And it should have a few methods to do things.

At the start that would be:

`initialize()`



---

`calibrate()`

`savecalibration()`

While running the experiment, on a frame-by-frame basis:

`lastsample()`

`testfixation()`

`comment()`

For data storage:

`startcollecting()`

`stopcollecting()`

Possibly at the end of the experiment, not sure though:

`shutdown()`

