
import numpy

class BinaryNearestMeanClassifierFactory(object):

    def __init__(self, scoringFunction):

        self.scoringFunction = scoringFunction
        self.productName     = "BinaryNearestMeanClassifier_" + self.scoringFunction.__name__

    def train(self, featureValues, classLabels):

        # Check dimensionality of training data
        (ns, nf) = featureValues.shape
        assert classLabels.shape == (ns, )

        # Check that the class labels are all booleans
        assert frozenset(classLabels) == frozenset([False, True])

        # Find the mean values for the False and True classes

        meanFalse = numpy.mean(featureValues[numpy.where(classLabels == False)], axis = 0)
        meanTrue  = numpy.mean(featureValues[numpy.where(classLabels == True )], axis = 0)

        return BinaryNearestMeanClassifier(self.scoringFunction, meanFalse, meanTrue)


class BinaryNearestMeanClassifier(object):

    def __init__(self, scoringFunction, meanFalse, meanTrue):

        self.scoringFunction = scoringFunction
        self.meanFalse       = meanFalse
        self.meanTrue        = meanTrue

    def score(self, samples):

        return numpy.apply_along_axis(lambda sample : self.scoringFunction(self.meanFalse, self.meanTrue, sample), 1, samples)

# V1, V2a, V2b, and V3 implement different distance metrics for the NMC classifiers.
#
# Note that the calculations as given here are normalized in such a way that the scores are invariant under
# rotations, translations, and scalings of the vectors {sample, meanFalse, meanTrue}.

def V1(meanFalse, meanTrue, sample):
    """
    This NMC distance metric projects the sample onto the line from meanFalse -> meanTrue, and normalizes the value;
    Points that project to meanFalse are scored as 0 (zero), points that project to meanTrue are scored as 1 (one).
    """
    return numpy.inner(sample - meanFalse, meanTrue - meanFalse) / numpy.inner(meanTrue - meanFalse, meanTrue - meanFalse)

def V2a(meanFalse, meanTrue, sample):
    """
    This NMC distance metric scores a sample by considering the (meanFalse, sample, meanTrue) triangle;
    The score is calculated as the length (Euclidean distance) of the (meanFalse, sample) side, divided over the distance of meanFalse meanTrue via 'sample'.
    """
    return numpy.linalg.norm(sample - meanFalse) / (numpy.linalg.norm(sample - meanFalse) + numpy.linalg.norm(sample - meanTrue))


def V2b(meanFalse, meanTrue, sample):
    """
    This NMC distance metric scores a sample by subtracting its Euclidean distance to meanTrue from its distance to meanFalse.
    The score is normalized to the distance between {meanFalse, meanTrue}.
    The iso-score lines in this case are hyperbolas.
    """
    return (numpy.linalg.norm(sample - meanFalse) - numpy.linalg.norm(sample - meanTrue)) / numpy.linalg.norm(meanTrue - meanFalse)


def V3(meanFalse, meanTrue, sample):
    """
    This NMC distance metric scores samples by considering a point that is halfway {meanFalse, meanTrue}, then calculating the
    cosine of the angle {sample, halfway, meanTrue}.
    Points towards meanTrue get a score of close to +1, while points towards meanFalse get a score close to -1.
    """
    halfway = 0.5 * (meanFalse + meanTrue)
    return numpy.inner(sample - halfway, meanTrue - halfway) / (numpy.linalg.norm(sample - halfway) * numpy.linalg.norm(meanTrue - halfway))
