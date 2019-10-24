# @Author 
# Sidney Cadot, update 2012/13 Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com

import numpy, random, json

class ExpressionDataset(object):
    def __init__(self, name, expressionData, geneLabels, patientClassLabels, patientLabels, checkNormalization, checkClassLabels = True):

        self.name               = name
        self.expressionData     = expressionData
        self.geneLabels         = geneLabels
        self.patientClassLabels = patientClassLabels
        self.patientLabels      = patientLabels

        # Expression-data should be two-dimensional
        assert len(self.expressionData.shape) == 2

        (self.numPatients, self.numGenes) = self.expressionData.shape
        # Perform some checks
        assert self.geneLabels.shape         == (self.numGenes, )
        assert self.patientClassLabels.shape == (self.numPatients, )
        assert self.patientLabels.shape      == (self.numPatients, )

        # Determine some vital statistics
        self.numPatientsGoodOutcome = sum(self.patientClassLabels == False)
        self.numPatientsBadOutcome  = sum(self.patientClassLabels == True)

        # Perform another check
        if checkClassLabels:
            assert self.numPatientsGoodOutcome + self.numPatientsBadOutcome == self.numPatients

        if checkNormalization and not self.checkIfExpressionDataProperlyNormalized():
            print("INFO: dataset %s is not properly normalized; normalizing now!" % self.name)
            self.performNormalization()

    def isCompatibleWith(self, other):
        assert isinstance(other, ExpressionDataset)

        if len(self.geneLabels) != len(other.geneLabels):
            return False

        return all(self.geneLabels == other.geneLabels)


    def extractPatientsByIndices(self, name, indices, checkNormalization = True, checkClasslabels = True):
        return ExpressionDataset(
            name,
            self.expressionData[indices,:],
            self.geneLabels,
            self.patientClassLabels[indices],
            self.patientLabels[indices],
            checkNormalization,
            checkClassLabels = checkClasslabels
        )

    # Gets the patient data of a specific set of genes.
    def extractGenesByIndices(self, name, indices, checkNormalization = True, checkClassLabels = True):
        return ExpressionDataset(
            name,
            self.expressionData[:,indices],
            self.geneLabels[indices],
            self.patientClassLabels,
            self.patientLabels,
            checkNormalization,
            checkClassLabels = checkClassLabels
        )

    def performNormalization(self):

        self.expressionData -= numpy.mean(self.expressionData, axis = 0)
        self.expressionData /= numpy.std (self.expressionData, axis = 0, ddof = 1)

    def checkIfExpressionDataProperlyNormalized(self):

        """ This method verifies that the expression-data for each of the genes
            is properly normalized. For each gene, the mean over all patients should be zero, and the standard deviation should be one.
        """

        # Find the maximal absolute deviation from the ideal value (mean: 0; stddev: 1), among all the patients.

        maxAbsMeanDeviationFromZero    = numpy.max(numpy.abs(numpy.mean(self.expressionData, axis = 0          ) - 0.0))
        maxAbsStandardDeviationFromOne = numpy.max(numpy.abs(numpy.std (self.expressionData, axis = 0, ddof = 1) - 1.0))

        meanOk              = maxAbsMeanDeviationFromZero    <= 1e-14
        standardDeviationOk = maxAbsStandardDeviationFromOne <= 1e-14

        return meanOk and standardDeviationOk

    def __str__(self):
        return "ExpressionDataSet(\"%s\"; %d genes; %d patients (good outcome: %d (%.2f %%), bad outcome: %d (%.2f %%)))" % (
                self.name, self.numGenes, self.numPatients,
                self.numPatientsGoodOutcome, float(self.numPatientsGoodOutcome) / float(self.numPatients) * 100.0,
                self.numPatientsBadOutcome , float(self.numPatientsBadOutcome)  / float(self.numPatients) * 100.0
            )

    # This function is needed for the Dao feature extractor
    def writeToFile(self, filename):
        #print("TODO: write to file") 
        f = open(filename, "w")
        L = list(self.patientLabels)
        f.write("Gene")
        f.writelines(["\t%s" % item for item in L])
        for g in range(0, len(self.geneLabels)):
            f.write("\n")
            l = list(self.expressionData[:, g])
            f.write(self.geneLabels[g])
            f.writelines(["\t%s" % item for item in l])
            #f.write("\n")
        f.close()

    def writeClasslabels(self, filename):
        f = open(filename, "w")
        L = list(self.patientLabels)
        f.writelines(["\t%s" % item for item in L])
        f.writelines(["\t%s" % item for item in self.patientClassLabels])
        f.close()

class FoldMap:

    def __init__(self, foldAssignments):

        self.foldAssignments = foldAssignments

    def toJsonExpression(self):

        return json.dumps(self.foldAssignments)


def MakeRandomFoldMap(dataset, numberOfFolds, repeatNr):

    assert numberOfFolds > 1

    # The "seed" is a tuple consisting of the dataset name, number of folds repeats, and repeat number.

    seed = (dataset.name, numberOfFolds, repeatNr)

    prng = random.Random(seed)

    # Order the patients by class, then by random number (which randomizes inside the class); keep a zero-based patient index

    ordering = sorted([(classLabel, prng.random(), patientIndex) for (patientIndex, classLabel) in enumerate(dataset.patientClassLabels)])

    # Keep only the patient label; the order is the imprtant thing, here.

    ordering = [patientIndex for (classLabel, randomValue, patientIndex) in ordering]

    # associate each patient with a fold number.

    patientIndexFoldNumberPairs = zip(ordering, [i % numberOfFolds + 1 for i in xrange(len(ordering))])

    # sort by patient index, and just keep the foldNr

    foldAssignments = [foldNr for (patientIndex, foldNr) in sorted(patientIndexFoldNumberPairs)]

    return FoldMap(foldAssignments)


def MergeExpressionDatasets(datasets, mergedDatasetName = None, checkNormalization=True, checkClassLabels = True):

    assert all([isinstance(dataset, ExpressionDataset) for dataset in datasets])

    if len(datasets) >= 1:
        geneLabels = datasets[0].geneLabels
    else:
        genelabels = numpy.array([])

    # Check that all datasets to be merged agree on their underlying gene labels.
    if checkClassLabels:
        assert all([all(dataset.geneLabels == geneLabels) for dataset in datasets])

    if mergedDatasetName is None:
        mergedDatasetName = "Merged(%s)" % ", ".join([dataset.name for dataset in datasets])

    patientLabels      = numpy.hstack([dataset.patientLabels      for dataset in datasets])
    patientClassLabels = numpy.hstack([dataset.patientClassLabels for dataset in datasets])
    expressionData     = numpy.vstack([dataset.expressionData     for dataset in datasets])

    # checkNormalization = True triggers the z-normalisation
    return ExpressionDataset(mergedDatasetName, expressionData, geneLabels, patientClassLabels, patientLabels, checkNormalization, checkClassLabels)

# To distinguish between indices and NCBI gene IDs or other IDs we put a prefix in front of each geneID. 
# Default is "Entrez_".
def HDF5GroupToExpressionDataset(group, checkNormalise = True, prefix="Entrez_"):
    
    assert group.name.startswith("/")

    datasetName        = group.name[1:]
    expressionData     = numpy.array(group["ExpressionData"])
    geneLabels         = numpy.array(group["GeneLabels"])
    patientClassLabels = numpy.array(group["PatientClassLabels"])
    patientLabels      = numpy.array(group["PatientLabels"])
    
    if not checkNormalise:
        print("Warning: z-Normalisation not guaranteed. Use checkNormalise = True!")

    if str(patientLabels.dtype).startswith('int'):
        patientLabels = numpy.array(["%s/%d" % (datasetName, patientLabel) for patientLabel in patientLabels])
    else:    
        patientLabels = numpy.array(["%s/%s" % (datasetName, patientLabel) for patientLabel in patientLabels])
    if str(geneLabels.dtype).startswith('int'):
        geneLabels    = numpy.array([prefix+"%d" % geneLabel for geneLabel in geneLabels])
    else:    
        if geneLabels[0].startswith(prefix):
            geneLabels    = numpy.array(["%s" % geneLabel for geneLabel in geneLabels])
        else:
            print("Gene labels ", geneLabels[0])
            print("Adding prefix.")
            geneLabels    = numpy.array([prefix+"%s" % geneLabel for geneLabel in geneLabels])
    
    assert len(set(patientClassLabels.tolist())) <= 2
     
    BAD_OUTCOME  = max(patientClassLabels)
    patientClassLabels = (patientClassLabels == BAD_OUTCOME) # Turn it into an array of bools

    ds = ExpressionDataset(datasetName, expressionData, geneLabels, patientClassLabels, patientLabels, checkNormalization = checkNormalise)

    print("NOTE: HDF5GroupToExpressionDataset -- read", ds)

    return ds
