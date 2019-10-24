# @Author 
# Sidney Cadot, Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com


from sklearn.metrics import roc_curve, auc
import numpy
# See http://en.wikipedia.org/wiki/Receiver_operating_characteristic for a good discussion of the ROC and AUC.
import itertools


def CalculateAUCandCI(scores, outcomes):
    auc = CalculateAUC(scores, outcomes)
    ci = CalculateCI(scores, outcomes)
    return (auc, ci)

def CalculateAUC(scores, outcomes):

    assert len(scores) == len(outcomes)
    n = len(scores)

    score_outcome = zip(scores, outcomes)
    score_outcome.sort()

    # We will start by picking a threshold above all
    # feature values; all samples would be classified as "negative".
    (FP, TP) = (0, 0)
    (previous_FP, previous_TP) = (FP, TP)

    TwiceArea = 0

    i = n - 1
    while i >= 0:
        # From now on we will count score_outcome[i] as a positive.
        # depending on its actual outcome, this will count as either a false Positive or a True Positive.
        if score_outcome[i][1]:
            TP += 1
        else:
            FP += 1

        # if this is the last sample visited of the group of equally-scoring
        # samples; determine its area contribution.
        if i == 0 or score_outcome[i][0] != score_outcome[i - 1][0]:
            TwiceArea += (FP - previous_FP) * (TP + previous_TP)
            (previous_FP, previous_TP) = (FP, TP)

        # proceed to next sample
        i -= 1

    aucVal = float(TwiceArea) / float(2 * TP * (n - TP))
    #fpr, tpr, thresholds = roc_curve(outcomes, scores)
    #tscikitsAuc = auc(fpr, tpr)
    #print("*********************************************")
    #print("Debug: auc", aucVal, "scikits", tscikitsAuc) 
    #print("*********************************************")

    return aucVal

# claculates for all possible scores the classification error when this score is taken as 
# threshold.
# if val <= threshold --> sample is classified as negative sample
# if val >  threshold --> sample is classified as positive sample
def CalculateClassificationError(scores, outcomes):

    #We define the classification error by
    # E = (FP+FN)/N * 100

    assert len(scores) == len(outcomes)
    n = len(scores)
    
    threshold_error = []
    for threshold in scores:
        idx_neg_scores = numpy.argwhere(scores <= threshold)[:, 0]
        FN = numpy.sum(outcomes[idx_neg_scores] == True)
        idx_pos_scores = numpy.argwhere(scores > threshold)[:, 0]
        FP = numpy.sum(outcomes[idx_pos_scores] == False)
        threshold_error.append([threshold, float(FP+FN)/float(n) * 100])

    return threshold_error

# calculates the concordance index (CI).
def CalculateCI(scores, outcomes):

    assert len(scores) == len(outcomes)
    idx = range(len(scores))    
    pairs = list(itertools.product(idx, idx))
    s = 0
    validPairs = 0
    for idx1, idx2 in pairs:
        if outcomes[idx1] > outcomes[idx2]:
            validPairs = validPairs + 1
            if scores[idx1] > scores[idx2]:
                s = s + 1
            elif scores[idx1] == scores[idx2]:
                s = s + 0.5
    ci = float(s)/validPairs
    
    return ci

 

## NOTE: the original results as published were performed using the code given below.
## The code is sound, but this way of calculating the AUC does not handle samples
## that have *exactly* the same score value properly.
##
## For that reason, it was replaced by the code above which does handle that case
## properly.
##
## Two samples having the same real-values scores is *extremeley* unlikely and we verified that
## this didn't occur in our experiments -- so those results stand. However, for future experiments\
## we should use the method given above.

#def CalculateAUC(sortedClassLabels):
#
#    assert frozenset(sortedClassLabels) == frozenset([False, True])
#
#    # True True True ....... False False False
#
#    # We start by classifying all samples as False;
#    #   this means we have zero False Positives and zero False Negatives.
#    #
#    # In terms of the ROC curve, this means we start in the point (0, 0) in (FPR, TPR) space.
#
#    height = 0
#    area   = 0
#
#    # One by one, we will consider each samples in the order of
#    # "most probably true" (highest score) to "least probably true"
#    # (lowest score).
#    #   From that point on, we will consider that sample a "negative".
#
#    for c in sortedClassLabels:
#        # Henceforth, we will count 'c' as a positive.
#        # It can either be a positive false or a true positive!
#        if c:
#            # true positive
#            height += 1
#        else:
#            # false positive
#            area += height
#
#    nPos = height # number of positives counted
#    nNeg = len(sortedClassLabels) - nPos
#
#    # We are unable to give a well-defined AUC value if all class labels are true, or all class labels are false.
#    if nPos == 0 or nNeg == 0:
#        return None
#
#    return float(area) / float(nPos * nNeg)
