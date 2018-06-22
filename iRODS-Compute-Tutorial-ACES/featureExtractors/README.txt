Feature Extractors
==================

SingleGeneFeatureExtractor, GeneSignatures: Benchmark Feature extractors.
        Each feature is one gene and its expression value is the feature value.
        The SingleGeneFeatureExtractor returns a ranked list of all genes in the data.
        In the classification only the top part of the list is used.
        The GeneSignatures return a set of genes that is employed to classify.

RandomGeneFeatureExtractor: Benchmark method.
        As SinglegeneFeatureExtractor, does not rank genes but resorts then randomly.

Winter/GeneRankFeatureExtrator: Pathway dependent gene ranking algorithm.
        Genes are ranked by googles page rank algorithm and an initial 
        discriminative score on the nodes:
        Winter: Correlation between gene's expression and patients' classlabels
        WinterTime: Correlation between gene's expression and patients' DMFS or RFS time
        GeneRank: absolute mean difference between gene's expression across the two patient classes.
        GeneRankTscore: t-statistic of the gene's expression across the two patient classes.

LeeFeatureExtractor: Pathway dependent feature extractor. 
        Each feature is a set of genes. The feature value is
        based on the average expression of all genes in a feature. The feature extractor
        returns a feature for each pathway. The features are ranked by their
        t-statitic.

ChuangFeatureExtractor: Network dependent feature extractor.
        Each feature is a connected subnetwork in the input network.
        The feature value is based on the average gene expression of member genes
        in a subnetwork. The features are ranked by the mutual information.

TaylorFeatureExtractor: Network dependent feature extractor.
        Determines significantly changed hubs.
        Features values are either the average expression difference between the hub and its interactors
        or
        Feature sets are the edges between the hub and its interactors. In this case feature values
        are the difference between the hub and the interactor.

DaoFeatureExtractor: Network dependent feature extractor.
        Each feature is a connected subnetwork in the input network.
        The feature value is the average gene expression of member genes.
        The features are ranked.

