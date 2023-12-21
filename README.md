# IntrepidEyeTracking

An object that implements some eye tracking functionality for the EyeLink, the LiveTrack Lightning, as well as a debug mode using the mouse.

The object will have a few properties:
- which eye-tracker mode to use
- toggle for tracking each eye
- window for accepting a fixation

And it should have a few methods to do things:

At the start that would be:

- IETinitialize()
- IETcalibrate()
- IETsavecalibration()

While running the experiment, on a frame-by-frame basis:

- IETlastsample()
- IETtestfixation()
- IETcomment()

For data storage:

- IETstartcollecting()
- IETstopcollecting()

Possibly at the end of the experiment, not sure though:

- IETshutdown()

