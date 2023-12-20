# IntrepidEyeTracking
Two sets of wrapper functions with identical names, purposes and output. One works with the EyeLink and one works with the LiveTrack Lightning.

What are the things we need?

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

Making a set of functions assumes that we are not using any kinds of objects.
