#! /usr/bin/env python

import numpy

# Make sure we can transparantly transfer NumPy types to and from R
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate() # In the new version of RPy2 you need to activate that feature.


def OneSided_Wilcoxon(x, y):
    """This function returns the P value of a paired (signed difference) Wilcoxon statistic"""

    (n_x, ) = x.shape
    (n_y, ) = y.shape

    assert n_x == n_y

    import rpy2.robjects as robjects

    wilcox = robjects.r["wilcox.test"]

    wilcox_result = wilcox(x, y, paired = True, alternative = "less")

    value = wilcox_result.rx2("p.value")
    value = value[0]

    return value


def Wilcoxon(x, y, pairedFlag):
    """This function returns the P value of a paired (signed difference) Wilcoxon statistic"""

    (n_x, ) = x.shape
    (n_y, ) = y.shape

    if pairedFlag:
        assert n_x == n_y

    import rpy2.robjects as robjects

    wilcox = robjects.r["wilcox.test"]

    wilcox_result = wilcox(x, y, paired = pairedFlag)

    value = wilcox_result.rx2("p.value")
    value = value[0]

    return value

def main():

    x = [19.84285182, 17.87394784, 12.06357909, 13.39278731, 13.03817053]
    y = [13.94414902, 13.14345403, 17.96745055, 13.93848477, 13.20006472]

    x = numpy.array(x)
    y = numpy.array(y)

    print(x)
    print(y)

    print(OneSided_Wilcoxon(x, y))

if __name__ == "__main__":
    main()
