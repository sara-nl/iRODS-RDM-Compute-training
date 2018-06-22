
The 'statistics' directory contains a number of utility classes to perform
statistical analysis:

* Statistics.py  -- implements the t-score statistic for unequal sample size
                    and unequal variance, and the Pearson correlation coefficient

* Wilcoxon.py    -- Implements the Wilcoxon "rank" test (both paired and unpaired variants).
                    NOTE: This is deferred to R, using the rpy2 package.

* AUC.py         -- Implements a function to calculate area-under-the-curve, given
                    sample scores and binary sample outcomes.

* PerformanceCurve.py -- Given a feature extractor, a classifier factory, a training expression
                         dataset, a testing expression dataset, and a list of feature counts,
                         the 'CalculateFeatureCountDependentPerformanceCurve' performs all necessary
                         steps to calculate the AUC curve that results from training a classifier
                         on the training dataset, then testing the trained classifier on the testing
                         dataset, for different numbers of features.

* Fisher.py -- This implementents the 'Fisher Exact' tests for the case of 2 binary classifications.
               The code reproduces the p-values as calculated by the one- and two-sided versions as
               implemented by R's "fisher.test" function.

               The calculation given here is exact, i.e., it is performed in terms of arbitrary-precision
               rational numbers, as provided by the "gmp" library via the Python package "gmpy".
