
The Python files in this directory implement three data types:

* "ExpressionDataset" encapsulates expression data, gene names, and sample names, as
  well as a number of useful operations on them, such as normalization, folding,
  merging, and reading expression data from an HDF5 file.

* "EdgeSet"s respresent sets of edges (between genes). It implements functionality
  to extract the nodes, shuffle the genes, and reading an EdgeSet from a "SIF" file.

  The EdgeSet is used to represent 'network' data (such as PPI networks).

* "GeneSetCollection" represents a collection of gene-sets. It implements functionality
  to extract the nodes, shuffle the genes, and readinf a GeneSetCollection from a file.

  The GeneSetCollection is used to represent 'pathway' data, i.e., a set of genes that is
  considered part of a single curated pathway. Note that any additional information (for
  example, the role of the genes in the pathway, or their relationship) is not represented
  by this type.

Updates:

* ExptressionDataset, do not always perform all checks, write expression data to file for the Dao method
* EdgeSet, add edgeweights, write network to file for Dao method
