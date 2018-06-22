
Some Notes on the "Lee Method" ~ Sidney Cadot ~ September 2011
==============================================================

The "Lee" method originates from the same group that proposed the "Chuang" method.
For this reason, there is one striking similarity in the methods, which is the scoring
calculation for the gene-modules found (dividing the sum of expressions by the square
root of the number of genes in the module).

The Chuang and Lee methods differ in their input data. Chuang uses a list of edges in a
protein/protein interaction graph, whereas Lee uses "pathways": sets of genes that are
known to be involved in a certain biological pathway.

The Lee method introduces the concept of a "CORG" -- a "Condition-Responsive Gene".
A CORG is defined as the subset of genes in a pathway whose combined expression delivers
good discriminative power for the disease phenotype.

ISSUES
======

There are some issues with the Lee method that are worth mentioning.

* The method is fully deterministic. Identical runs of the Lee feature extraction method
  will yield identical CORGs.

* As is the case for the Chuang method, the Lee paper [1] is silent on the issue of nodes
  within the pathways for which no expression data is known. In case of the Lee method,
  the solution is fortunately obvious: we simply discard those genes during training for
  which we have no expression data.

* The CORG selection algorithm yields 1 CORG per pathway; the CORG is a subset
  of the pathway genes. The Lee method prescribes a rather complicated way of
  selecting the genes within the pathway that are to be part of the CORG, based
  on ordering them by their individual t-scores and traversing the list in either
  front-to-back or back-to-front order, and adding genes until the CORG t-statistic
  starts to decrease. Although we didn't quite try it, it is quite
  easy to do a more elaborate search to identify CORGs that have better performance,
  e.g. by always searching in both front-to-back and back-to-front orders, and
  not stopping at the first performance decrease. Such a method would still have
  a worst-case performance that is linear in the number of genes (as does the current
  algorithm) but would in many cases find a "better" CORG than the current method.

* As with the Chuang method, the module activation is calculated as the sum of the
  normalized expressions of the genes, divided by the square root of the number of
  genes in the module. There appears to be no justification for dividing by sqrt(n).
  Also, it is noted that pathways where the expression of some constituent genes
  correlate negatively will actually be scored as "less active".

REFERENCES
==========

[1] Inferring Pathway Activity toward Precise Disease Classification
    Eunjung Lee, Han-Yu Chuang, Jong-Won Kim, Trey Ideker, Doheon Lee
    PLoS Computational Biology November 2008 Volume 4 Issue 11
