import numpy as np

def gazeInFixationWindow(sample):

    # sample = self.lastsample() # now from input
    # check_samples = self.getSamplesToCheck() # now set manually here:
    check_samples = ['average']

    for sk in check_samples:
        if sk in sample.keys():
            # do the test?
            if any(np.isnan(sample[sk])):
                return(False)
        else:
            # sample to check not in the sample data:
            return(False)

    # for key in sample.keys():
    #     if key in check_samples:
    #         d = np.sqrt(np.sum(np.array(sample[key])**2))
    #         # if d > self.fixationWindow:
    #         if d > 2:
    #             infix = False

    return(True)


sample = {'average':np.array([np.nan, np.nan])}
print(gazeInFixationWindow(sample))