# Intrepid 2a EyeTracking

This provides a psychopy-compatible `EyeTracker` object that can be used to interact with either an EyeLink or a LiveTrack eye-tracker. We also plan on implementing a dummy mouse tracker, to be able to test/debug the behavioral side of experiments without an eye-tracker.

## EyeTracker object initialization

The object will have a few properties:

- which eye-tracker mode to use
- toggle for tracking each eye
- window for accepting a fixation
- the psychopy window used for the experiment (the LiveTrack version will use that for calibration, the Eyelink version will use it convert EyeLink stuff back to dva properly)
- a file folder to store eye-tracker data in
- specify the sample mode for gaze samples

These properties can be set when initializing the object, which makes a call to each the following 4 functions:

### `setEyetracker()`

**arguments:**

- tracker: _string_: ['eyelink', 'livetrack', 'mouse']

**returns:**

Nothing, but raises a Warning for incorrect input, which will stop the experiment and print the warning.

> This tells the EyeTracker object which kind of eye-tracker to use.

### `trackEyes()`

**arguments:**

- trackEyes: _list of 2 booleans_: left and right eye

**returns:**

Nothing, but raises a Warning for incorrect input, which will stop the experiment and print the warning.

> This tells the eye-tracker which eyes are to be monitored. They will both be used for instantaneous gaze samples, and stored in the raw eye-tracking data files.

### `setFixationWindow()`

**arguments:**

- fixationWindow: _number_ (float, int, ...) setting the maximum deviation from the fixation point in the units of the psychopy window

**returns:**

Nothing, but raises a Warning for incorrect input, which will stop the experiment and print the warning.

> We've previously talked about setting this to 2 dva, but maybe we should reduce this to 1.5 dva.

### `setPsychopyWindow()`

**arguments:**

- psychopyWindow: _psychopy window object_ assumes that the psychopy window has the unit set to degrees

**returns:**

Nothing, but raises a Warning for incorrect input, which will stop the experiment and print the warning.

> By default the psychopy window should be in degrees visual angle (dva, which they call `deg`). For the EyeLink _I think_ we need a window object using pixels, with the top-left corner at (0,0) and y-coords increasing when going down on the screen.

### `setFilefolder()`

**arguments:**

- filefolder: _string:_ the path to an **existing** folder to store raw eye-tracking data files (and for the LiveTrack: calibration parameters), if filefolder is a string of length 0 ('') no files will be stored (and a note is printed)

**returns:**

- Nothing, but raises an error if it is not a valid path.

### `setSamplemode()`

**argments:**

- samplemode: _string:_ ['both', 'left', 'right', 'average']

**returns:**

Nothing, but raises an error if no valid samplemode is set.

## Eye-Tracker initialization and calibration

At the start of the experiment we need to get everything ready, using initialization and then intermittently we need to do calibration. So those two steps are split into two functions.

### `initialize()`

**arguments:**

None

**returns:**

Nothing... but, perhaps this should be in a try/catch block (or several of them) to raise an Error when something goes wrong.

> This method sets up a connection to the eye-tracker, and makes it ready for the next step: calibration.

---

[below this line: not fully implemented yet]

### `calibrate()`

**arguments:**

None

**returns:**

Nothing?

> This function does the actual calibration of the eye-tracker (except for the dummy mouse tracker).

### `savecalibration()`

**arguments:**

None

**returns:**

Nothing... but/and:

> This function is useless for the EyeLink, so perhaps it should be combined with the LiveTrack version of doing the calibration, and be an internal function only.

## Running the experiment:

While running the experiment, on a frame-by-frame basis:

### `lastsample()`

**arguments:**

None

**returns:**

A dictionary with the last gaze sample, in the format ... (defined somewhere else)

### `waitForFixation()`

**arguments:**

- fixationPoint: _tuple of numbers:_ [X,Y] coordinates of the desired fixation in the units of the psychopy window, defaults to (0,0)
- duration: _number:_ (float or int) duration (in seconds) that the fixation point has to be fixated, on each consecutive frame in that period
- timeout: _number:_ (float or int) if the fixation point is not fixated for this amount of time (in seconds), the procedure times out

**returns:**

- _boolean:_ True: participant fixated the point, False: participant did not fixate the point within timeout seconds

> This waits for participants to fixate a point, e.g. to start a trial

### `driftFixation()`

**arguments:**

None

> This function stores an eye-tracker offset to apply to samples to return to the experiment. It is a form of online drift correction, that allows for some head movement without having to do a new calibration. This will only give (somewhat) accurate gaze samples at the fixation point used. Therefore, this should only be used for experiment that require fixating some point, not for experiments that where tracking more free eye-movements is important.

**returns:**

Nothing

### `comment()`

**arguments:**

- message: _string_ A message to be stored in the raw data file, right now / as soon as possible. This is primarily useful for segmenting raw eye-tracking data, so we can cut out trials, and events withing trials (stimulus onset / offset, and so on).

**returns:**

Nothing

## Raw data storage:

### `openFile()`

**arguments:**

- filename: _string:_ optional filename for use within the filefolder path specified on initialization of the object

**returns:**

Nothing, but raises a warning if the file can't be opened.

> The file name is stored in the filefolder specified when initializing the EyeTracker object. If no filename is specified, a standard filename is used, appended with an integer representing the number of files opened for the current instantiation of the object.

### `startCollecting()`

**arguments:**

None

**returns:**

Nothing

> This function starts storing data in an open file.

### `stopCollecting()`

**arguments:**

None

**returns:**

Nothing

> This function stops storing data in an open file.

### `closeFile()`

**arguments:**

None

**returns:**

Nothing, but raises a warning if the file can't be closed.

> This function closes a data file, if there is an open file. If there is no open file, the function does nothing.


## Closing the object

### `shutdown()`

**arguments:**

None

**returns:**

Nothing

> This function closes all objects, connections and files that were used (such as raw data files) and can be closed, depending on the eye-tracker used. In the case of the EyeLink it also downloads all closed data files.
