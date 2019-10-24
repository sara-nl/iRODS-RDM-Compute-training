# @Author 
# Sidney Cadot, update in 2012/13 Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com

import random

class GeneSetCollection:

    def __init__(self, name, geneSets, geneSetsNames, release):

        self.name     = name
        self.geneSets = geneSets
        self.geneSetsNames = geneSetsNames
        self.release = release

    def getNodes(self):

        return frozenset.union(*[frozenset(s) for s in self.geneSets])

    def makeShuffle(self, seed = 0):

        prng = random.Random(seed)
        nodes = sorted(frozenset.union(*[frozenset(s) for s in self.geneSets]))
        shuffled_nodes = nodes[:] # make a copy
        prng.shuffle(shuffled_nodes)

        return dict(zip(nodes, shuffled_nodes))

    def makeShuffledVersion(self, name, shuffle):

        shuffledGeneSets = []
        for geneSet in self.geneSets:

            shuffledGeneSet = [shuffle[gene] for gene in geneSet]
            shuffledGeneSets.append(shuffledGeneSet)

        return GeneSetCollection(name, shuffledGeneSets, self.geneSetsNames, self.release)

    def writeGeneSetCollection(self, filename):
        """
        writes a space-separated file:
            NAME pw1
            gene1 gene2 gene3 ...
            NAME pw2
            gene1 gene2 gene3 ...
        """
        lines = []
        for idx in range(len(self.geneSets)):
            if self.geneSetsNames != []:
                lines.append('NAME '+self.geneSetsNames[idx]+'\n')
            lines.append(" ".join(map(str, self.geneSets[idx]))+'\n')

        f = open(filename, 'w')
        f.writelines(["%s" % item  for item in lines])
        f.close()
        

def makeGeneSetCollection(name, geneSets, geneSetsNames, release):
    return GeneSetCollection(name, geneSets, geneSetsNames, release)

def ReadGeneSetCollection(geneSetCollectionName, filename, prefix = None):

    f = open(filename)

    geneSets = []
    geneSetsNames = []
    release = ''

    for line in f:

        line = line.rstrip("\r\n")

        if len(line) == 0:
            continue # Ignore empty lines.
        
        elif line.startswith("REALEASE"):
            release = line

        elif line.startswith("NAME"):
            geneSetsNames.append(line.replace("NAME ", ""))
            continue

        else:
            geneSet = line.split()
            assert len(geneSet) > 0
            assert len(geneSet) == len(set(geneSet)) # make sure they are all different
        
            #find common prefix
            letters = zip(*geneSet)
            common = "".join([x[0] for x in letters if x==(x[0],)*len(x)])
            #geneSet = map(int, geneSet) # make sure they are all integers.
            if prefix != None and common != prefix:
                geneSet = [prefix + str(gene) for gene in geneSet]

            geneSets.append(geneSet)

    f.close()

    print("NOTE: ReadGeneSetCollection(\"%s\", \"%s\"): read %d genesets." % (geneSetCollectionName, filename, len (geneSets)))

    return GeneSetCollection(geneSetCollectionName, geneSets, geneSetsNames, release)
