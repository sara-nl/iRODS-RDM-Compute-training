# @Author 
# Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com

import numpy, json
import random

# Difference between the two classes:
#
#     SingleGeneFeatureExtractorFactory: receives a training dataset and determines the possible features and their ranking
#     SingleGeneFeatureExtractor: receives an order of features and determines their feature values given a dataset

class RandomGeneFeatureExtractorFactory(object):

    productName = "RandomGeneFeatureExtractor"

    def train(self, dataset):

        #generate a random rodering of all genes in the data
        seed = (dataset.name)
        prng = random.Random(seed)

        ordering = sorted([(prng.random(), geneIndex) for geneIndex in range(len(dataset.geneLabels))])

        # Determine a list of the indexes of the most discriminative genes,
        #   i.e. the gene indexes re-ordered by absolute value of the corresponding t-statistic.
        #
        # NOTE: the minus sign before the "abs" is to get the highest-scoring genes at the start of the list.

        featureGeneIndices = [idx for (number, idx) in ordering]
        featureGeneIndices = map(int, featureGeneIndices) # make sure that the elements are regular ints, not NumPy types.

        return RandomGeneFeatureExtractor(dataset.geneLabels, featureGeneIndices)


class RandomGeneFeatureExtractor(object):
    name               = "RandomGeneFeatureExtractor"
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
