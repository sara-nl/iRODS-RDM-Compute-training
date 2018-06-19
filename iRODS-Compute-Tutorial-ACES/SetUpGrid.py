# @Author 
# Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com
# July 2013
import sys, os, h5py, sqlite3, json, numpy, itertools
import subprocess

# Input of primary and secondary datasets

from datatypes.ExpressionDataset import HDF5GroupToExpressionDataset
from datatypes.ExpressionDataset import MakeRandomFoldMap
from datatypes.GeneSetCollection import ReadGeneSetCollection

# Feature-extraction algorithms

from featureExtractors.SingleGenes.SingleGeneFeatureExtractor import SingleGeneFeatureExtractorFactory
from featureExtractors.SingleGenes.RandomGeneFeatureExtractor import RandomGeneFeatureExtractorFactory
from featureExtractors.Lee.LeeFeatureExtractor                import LeeFeatureExtractorFactory

# Classifiers

from classifiers.BinaryNearestMeanClassifier                  import BinaryNearestMeanClassifierFactory, V1, V2a, V2b, V3
from statistics.PerformanceCurve import CalculateFeatureCountDependentPerformanceCurve, CalculateFeatureCountDependentPerformance

import random

def CombineData():
    """
    Combines the data, methods and parameters for the Performance and Overlap evaluation.
    """
    datasets = ['U133A_combat_DMFS']
    pathways = ['nwGeneSetsKEGG', 'nwGeneSetsMsigDB']

    PathwayFeatureExtractorSpecificParams = [('Lee', None)]
    SingleGene = [('SingleGenes', None), ('RandomGenes', None)]

    #Combine algos with sec data
    NetworkDataAndFeatureExtractors = list(itertools.product(PathwayFeatureExtractorSpecificParams, pathways))
    NetworkDataAndFeatureExtractors.extend(list(itertools.product(SingleGene, [None])))
    #Combine FEs with data and number of shuffles
    DataAndFeatureExtractors = list(itertools.product(datasets, NetworkDataAndFeatureExtractors, [None]))

    return DataAndFeatureExtractors

def SetUpRun(dataset, network, method, datafile = "4851460", datapath = '..'):

    #get data from figshare
    # wget -P data/ https://ndownloader.figshare.com/files/4851460
    #print "Downloading data from figshare."
    #PATH = "data/"
    #wget = ["wget", "-P", PATH, "https://ndownloader.figshare.com/files/4851460"]  
    #proc = subprocess.Popen(wget, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            #stderr = subprocess.PIPE)
    #output, err = proc.communicate()  
  
    #get dataset
    f = h5py.File(datapath+'/'+datafile)
    # The hdf5 file contains several datasets, fetch the one we indicated 
    data = [HDF5GroupToExpressionDataset(f[group]) for group in f.keys() if dataset in group][0]
    f.close()

    #get network
    if network == "nwGeneSetsKEGG":
        net   = ReadGeneSetCollection("KEGGpw" , datapath+"/KEGG1210_PathwayGeneSets_Entrez.txt" , "Entrez_")
    elif network == "nwGeneSetsMsigDB":
        net = ReadGeneSetCollection("MsigDBpw" , datapath+"/C2V3_PathwayGeneSets_Entrez.txt"     , "Entrez_")
    elif network == "nwEdgesKEGG":
        net = ReadSIF("KEGG"  , datapath+"/KEGG_edges1210.sif" , "Entrez_")
    elif network == None:
        net = None
        print "SG no network"
    else:
        raise Exception("Network not known. Add network in SetUpGrid/SetUpRun.")

    #get featureselection method
    if method == "Lee":
        featureSelector = LeeFeatureExtractorFactory()
    elif method.startswith('SingleGenes'):
        featureSelector = SingleGeneFeatureExtractorFactory()
    elif method.startswith('RandomGenes'):
        featureSelector = RandomGeneFeatureExtractorFactory()
    else:
        raise Exception("Method not known. Add method in SetUpGrid/SetUpRun.")

    #get classifier
    classifiers = [
        BinaryNearestMeanClassifierFactory(V1),
    ]

    return (data, net, featureSelector, classifiers, None)

def RunInstance(data, net, featureSelector, special, classifiers, repeat, nrFolds, fold, shuffleNr, survTime = None, TaylorParam = True):

    #in case if the inner loop the dataset name has an additional tag.
    if "training" in data.name:
        dName = "_".join(data.name.split('_')[:len(data.name.split('_'))-2])
    else:
        dName = data.name

    #split datasets
    dsTraining, dsTesting, foldMap = splitData(data, fold, repeat, nrFolds)    

    #select features
    if featureSelector.productName in ["SingleGeneFeatureExtractor", "RandomGeneFeatureExtractor"]:
        featureExtractor = featureSelector.train(dsTraining)
    elif special == None: #Chuang, Dao, Lee
        featureExtractor = featureSelector.train(dsTraining, net)
    else:
        raise Exception("Method not known. Add method in SetUpGrid/SetUpRun.")

    #train classifiers and produce AUC values with the testing dataset
    maxFeatureCount = 400
    AucAndCi = {}
    for CF in classifiers:
        print "-->", CF.productName
        featureCounts = [fc for fc in featureExtractor.validFeatureCounts if fc <= maxFeatureCount]
        nf_to_auc = CalculateFeatureCountDependentPerformanceCurve(
           featureExtractor,
           CF,
           (dsTraining, dsTesting),
           featureCounts
        )
        AucAndCi[CF.productName] = nf_to_auc
    
    #return the resulting features, and classification results
    if net == None:
        return (data.name, featureExtractor.name, None, None, featureExtractor.toJsonExpression(), AucAndCi)    
    else:
        return (data.name, featureExtractor.name, net.name, None, featureExtractor.toJsonExpression(), AucAndCi)

def splitData(data, fold, repeat, nrFolds):
    #split datasets
    foldMap = MakeRandomFoldMap(data, nrFolds, repeat)
    foldList = range(0, nrFolds)
    dsTraining = data.extractPatientsByIndices("%s_fold-%d-of-%d_training" % (data.name, fold,
        len(foldList)), numpy.array(foldMap.foldAssignments)-1 != fold, checkNormalization = False)
    dsTesting = data.extractPatientsByIndices("%s_fold-%d-of-%d_testing"  % (data.name, fold,
        len(foldList)), numpy.array(foldMap.foldAssignments)-1 == fold, checkNormalization = False)
    
    return dsTraining, dsTesting, foldMap

def NextItem(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    it = itertools.chain([first], iterable)
    return first, it

def getDoneTokens(db, experiment):
    """
    Sort all done Tokens according to experiment.
    db  :   dictionary item['_id']: item
    """    

    finishedTokens  = []
    pendingTokens   = []

    otherDocs = []
    pending = []
    for item in db:
        doc = db[item]
        if 'output' in doc.keys():
            if item.startswith(experiment):
                finishedTokens.append(doc)
        elif "lock" in doc.keys():
            if doc["lock"] > 0 and doc["done"] == 0:
                pendingTokens.append(doc)

    return finishedTokens, pendingTokens

def resetTokens(ids, db):

    for ID in ids:
        token = db.get(ID)
        scrub = token['scrub_count']
        updateContent = {'lock': 0, 
            'scrub_count' : scrub+1}
        token.update(updateContent)
        db.save(token)
