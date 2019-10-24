# @Author 
# Sidney Cadot, Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com

import numpy

from statistics.AUC import CalculateAUCandCI

def DetermineAUCandCI(featureExtractor, nf, classifierFactory, (dsTraining, dsTesting), ERlabels = None):

    if featureExtractor.name in ["SCPunsupervisedFeatureExtractor", "SCPFeatureExtractor", "PatsialouGeneSignature", "VantVeerGeneSignature", "ErasmusMCGeneSignature", "ErasmusMCProbeSignature"]:
        assert nf == featureExtractor.validFeatureCounts
    else:
        assert nf in featureExtractor.validFeatureCounts

    # Train a classifier on the features extracted from the TRAINING dataset

    if featureExtractor.name in ["SCPunsupervisedFeatureExtractor", "SCPFeatureExtractor", "PatsialouGeneSignature", "VantVeerGeneSignature", "ErasmusMCGeneSignature", "ErasmusMCProbeSignature"]:
        if "FourClassNearestMeanClassifier_" in classifierFactory.productName:
            classifier = classifierFactory.train(featureExtractor.extract(dsTraining), dsTraining.patientClassLabels, ERlabels)
        else:
            classifier = classifierFactory.train(featureExtractor.extract(dsTraining), dsTraining.patientClassLabels)
    elif "FourClassNearestMeanClassifier_" in classifierFactory.productName:
        classifier = classifierFactory.train(featureExtractor.extract(dsTraining, nf), dsTraining.patientClassLabels, ERlabels)
    else:
        classifier = classifierFactory.train(featureExtractor.extract(dsTraining, nf), dsTraining.patientClassLabels)
    if classifier is None:
        return None

    # Evaluate the classifier performance on the features extracted from the 'testing' dataset

    if featureExtractor.name in ["SCPunsupervisedFeatureExtractor", "SCPFeatureExtractor", "PatsialouGeneSignature", "VantVeerGeneSignature", "ErasmusMCGeneSignature", "ErasmusMCProbeSignature"]:
        scores = classifier.score(featureExtractor.extract(dsTesting))
    else:
        scores = classifier.score(featureExtractor.extract(dsTesting, nf))

    assert isinstance(scores, numpy.ndarray)
    assert all(numpy.isfinite(scores))

    assert scores.shape == dsTesting.patientClassLabels.shape
    assert dsTesting.patientClassLabels.dtype == bool

    return CalculateAUCandCI(scores, dsTesting.patientClassLabels)

def CalculateFeatureCountDependentPerformanceCurve(featureExtractor, classifierFactory, (dsTraining, dsTesting), featureCounts, ERlabels = None):
    # walk over the number of features as given in 'featureCounts'.
    # For each of the number of features, determine the auc value.
    # Return a map of feature-count to corresponding AUC value.

    print("-->", dsTraining.name, dsTesting.name)

    result = {}
    for nf in featureCounts:
        auc, ci = DetermineAUCandCI(featureExtractor, nf, classifierFactory, (dsTraining, dsTesting), ERlabels)
        if auc is not None:
            assert numpy.isfinite(auc)
            assert 0.0 <= auc <= 1.0
            result[nf] = [auc, ci]

    return result

def CalculateFeatureCountDependentPerformance(featureExtractor, classifierFactory, (dsTraining, dsTesting), ERlabels = None):
    print("-->", dsTraining.name, dsTesting.name)

    result = {}
    auc, ci = DetermineAUCandCI(featureExtractor, featureExtractor.validFeatureCounts, classifierFactory, (dsTraining, dsTesting), ERlabels = ERlabels)
    if auc is not None:
        assert numpy.isfinite(auc)
        assert 0.0 <= auc <= 1.0
        result[featureExtractor.validFeatureCounts] = [auc, ci]

    return result

