
import numpy, json
from statistics.Statistics import tStatisticForUnequalSampleSizeAndUnequalVariance

# Difference between the two classes:
#
#     SingleGeneFeatureExtractorFactory: receives a training dataset and determines the possible features and their ranking
#     SingleGeneFeatureExtractor: receives an order of features and determines their feature values given a dataset

class SingleGeneFeatureExtractorFactory(object):

    productName = "SingleGeneFeatureExtractor"

    def train(self, dataset):

        # Retrieve the subset of expression data for patients who are classified as True resp. False.

        cTrue  = dataset.expressionData[                  dataset.patientClassLabels ]
        cFalse = dataset.expressionData[numpy.logical_not(dataset.patientClassLabels)]

        # Compare expression value for each of the genes, between the two classes.
        # Highly differential expressed genes have a large absolute t-statistic.

        # Note: order is important!
        tStatistic = tStatisticForUnequalSampleSizeAndUnequalVariance(cTrue, cFalse)

        # Determine a list of the indexes of the most discriminative genes,
        #   i.e. the gene indexes re-ordered by absolute value of the corresponding t-statistic.
        #
        # NOTE: the minus sign before the "abs" is to get the highest-scoring genes at the start of the list.

        featureGeneIndices = numpy.argsort(-numpy.abs(tStatistic))
        featureGeneIndices = map(int, featureGeneIndices) # make sure that the elements are regular ints, not NumPy types.

        return SingleGeneFeatureExtractor(dataset.geneLabels, featureGeneIndices)


class SingleGeneFeatureExtractor(object):
    name               = "SingleGeneFeatureExtractor"
    def __init__(self, geneLabels, featureGeneIndices):
        self.geneLabels         = geneLabels
        self.featureGeneIndices = featureGeneIndices
        self.validFeatureCounts = range(1, len(self.featureGeneIndices) + 1)

    # k - number of features
    def extract(self, dataset, k):
        # Make sure we have the same idea of our source data
        assert all(dataset.geneLabels == self.geneLabels)

        assert k in self.validFeatureCounts

        # return expression values for k-most-significant features
        return dataset.expressionData[:, self.featureGeneIndices[:k]]

    def toJsonExpression(self):
        return json.dumps((self.__class__.__name__, [geneLabel for geneLabel in self.geneLabels], [int(featureGeneIndex) for featureGeneIndex in self.featureGeneIndices]))
