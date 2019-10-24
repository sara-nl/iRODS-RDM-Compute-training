
import numpy
import json
from statistics.Statistics import tStatisticForUnequalSampleSizeAndUnequalVariance
from datatypes.GeneSetCollection import GeneSetCollection

class LeeFeatureExtractorFactory(object):

    # Specify the product of this factory. Useful for printing.
    productName = "LeeFeatureExtractor"

    @staticmethod
    def scoreCORG(dataset, corg):

        # "CORG" is short for: "Condition-Responsive Gene".
        # It is defined as "the subset of genes in the patway whose combined expression delivers
        #      optimal discriminative power for the disease phenotype."

        assert isinstance(corg, list)

        # To calculate the activation valuess for each patient, we sum the (pre-normalized) activation
        # values of the genes within the pathway, and divide by the square root of the number of genes
        # in the pathway.

        # The division by sqrt(n) rather than simply by n follows the paper.
        # There does not seem to be a good reason for this.

        activations = numpy.sum(dataset.expressionData[:,corg], axis = 1) / numpy.sqrt(len(corg))
        activations = activations.reshape(-1, 1)

        # Select this CORGs activation value for the "true outcome" and "false outcome" patients,
        # separately. This yields two sample-sets.

        cTrue  = activations[                  dataset.patientClassLabels ,:]
        cFalse = activations[numpy.logical_not(dataset.patientClassLabels),:]

        # Determine the t-score of both sets that is a measure for the
        # discriminative power of this particular CORG.

        tStatistic = tStatisticForUnequalSampleSizeAndUnequalVariance(cTrue, cFalse)

        # The previous function generates a length-1 array. Verify this.

        assert tStatistic.shape == (1, )

        # Return the actual t-score value as found in the first element.

        return tStatistic[0]

    def train(self, dataset, network):

        # Prepare a gene label-to-index lookup table.

        geneLabelToIndex = dict(zip(dataset.geneLabels, xrange(len(dataset.geneLabels))))

        # The network is a GeneSetCollection, containing a list of gene-lists.
        # Each gene-list represents a pathway.

        assert isinstance(network, GeneSetCollection)

        # We will now iterate over each of the gene-sets. The goal is to determine a subset of
        # the genes that is highly dicriminative with regard to the patient outcome.

        features = []

        for geneSet in network.geneSets:

            # NOTE: We discard those genes in the pathway for which we do not have expression data.

            availableGenes = numpy.array([geneLabelToIndex[geneLabel] for geneLabel in geneSet if geneLabel in geneLabelToIndex])

            if len(availableGenes) == 0:
                # This geneset has no genes for which we have data! Skip it.
                continue

            cTrue  = dataset.expressionData[:,availableGenes][                  dataset.patientClassLabels ]
            cFalse = dataset.expressionData[:,availableGenes][numpy.logical_not(dataset.patientClassLabels)]

            # Note that the order of cTrue / cFalse does not influence the ordering of the genes.
            tStatistic = tStatisticForUnequalSampleSizeAndUnequalVariance(cTrue, cFalse)

            if numpy.mean(tStatistic) < 0:
                idx = numpy.argsort(+tStatistic)
            else:
                idx = numpy.argsort(-tStatistic)

            sortedCandidateGenes = availableGenes[idx]
            sortedCandidateGenes = map(int, sortedCandidateGenes) # make sure they're regular ints

            tStatistic = tStatistic[idx]

            # We now have an array of candidate genes, sorted by t-score.
            # Next, we will consider each non-empty list up to length n to determine
            # the "optimal" set of genes to use as CORG.
            # As soon as the CORG score decreases we will stop!

            (optimalCorgScore, optimalCorg) = (None, None)

            for n in xrange(1, 1 + len(sortedCandidateGenes)):

                # Consider CORG that consists of 'n' genes.

                corg = sortedCandidateGenes[:n]
                corgScore = self.scoreCORG(dataset, corg)

                # Check if the new CORG is more discriminative that the previous optimal corg.

                if (optimalCorgScore is None) or (optimalCorgScore >= 0 and corgScore > optimalCorgScore) or (optimalCorgScore < 0 and corgScore < optimalCorgScore):
                    (optimalCorgScore, optimalCorg) = (corgScore, corg)
                else:
                    # We leave the loop as soon as we find a CORG that descreases the CORG score.
                    # Note that the overall performance may be better if we leave the 'break' out.
                    break

            features.append((optimalCorgScore, optimalCorg))

        idx = numpy.argsort([-numpy.abs(optimalCorgScore) for (optimalCorgScore, optimalCorg) in features])

        corgs = [frozenset(optimalCorg) for (optimalCorgScore, optimalCorg) in features]

        corgs = numpy.array(corgs)

        # sort by absolute t-score (highest scores go first)
        corgs = corgs[idx]

        features = []
        for corg in corgs:
            if corg not in features:
                features.append(corg)

        if len(features)  < len(corgs):
            print("WARNING: removed duplicate corgs (%d corgs -> %d features)" % (len(corgs), len(features)))

        return LeeFeatureExtractor(dataset.geneLabels, features)


class LeeFeatureExtractor(object):

    name               = "LeeFeatureExtractor"

    def __init__(self, geneLabels, features):
        self.geneLabels         = geneLabels
        self.features           = features
        self.validFeatureCounts = range(1, len(self.features) + 1)

    @staticmethod
    def score(expressionData, feature):
        # The division by sqrt(n) rather than simply by n follows the paper.
        # There does not seem to be a good reason for this.
        return numpy.sum(expressionData[:, list(feature)], axis = 1) / numpy.sqrt(len(feature))

    def extract(self, dataset, k):

        assert all(dataset.geneLabels == self.geneLabels)
        assert k in self.validFeatureCounts

        # Return the network scores for the k best subnetworks
        return numpy.transpose(numpy.array([self.score(dataset.expressionData, feature) for feature in self.features[:k]]))

    def toJsonExpression(self):

        return json.dumps((self.__class__.__name__, [geneLabel for geneLabel in self.geneLabels], [sorted(feature) for feature in self.features]))
