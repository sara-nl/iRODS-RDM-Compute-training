
Some Notes on the "Single Genes" method ~ Sidney Cadot ~ September 2011
=======================================================================

The Single Genes (SG) feature extraction method aims to identify a subset
of the available genes that have a high discriminative value with regard
to outcome when the expression values are used as inputs to a classier
algorithm.

To this end, all genes are ordered by absolute t-score; this is an
indicator for how well the gene's expression, taken by itself,
discriminates between patients with a "good outcome" vs a "bad outcome".

By taking the set of k most discriminative genes, in this sense, we
get a k-size feature vector that can be used as input to a classifier algorithm.

Some Notes on the "Random Genes" method ~ Christine Staiger ~ March 2012
=============================================================================
Genes are randomly sorted. the subset of genes for classificationare taken 
from the top.
