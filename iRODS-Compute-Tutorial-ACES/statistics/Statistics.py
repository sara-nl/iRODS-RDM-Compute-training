import numpy

def tStatisticForUnequalSampleSizeAndUnequalVariance(matrix1, matrix2):

    # T-scores are normally calculated between two single sample vectors.
    # Here, we generalize that to allow simultaneous t-statistic calculation
    # for multiple pairs of sample vectors.

    (ns1, nf1) = matrix1.shape
    (ns2, nf2) = matrix2.shape

    # the number of features must be equal between the two matrices
    assert nf1 == nf2

    mean1 = numpy.mean(matrix1, axis = 0)
    mean2 = numpy.mean(matrix2, axis = 0)

    var1 = numpy.var(matrix1, axis = 0, ddof = 1)
    var2 = numpy.var(matrix2, axis = 0, ddof = 1)

    tStatistic = (mean1 - mean2) / numpy.sqrt(var1 / ns1 + var2 / ns2)

    return tStatistic


def PearsonCorrellationCoefficient(x, y):

    """Return the Pearson correllation coefficient of two vectors."""

    assert isinstance(x, numpy.ndarray)

    (nx, ) = x.shape
    (ny, ) = y.shape

    assert nx == ny

    n = nx

    mx = numpy.mean(x)
    my = numpy.mean(y)

    sx = numpy.std(x, ddof = 1)
    sy = numpy.std(y, ddof = 1)

    corrcoef = numpy.inner(x - mx, y - my) / (sx * sy) / (n - 1)

    return corrcoef
