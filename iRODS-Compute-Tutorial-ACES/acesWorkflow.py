from SetUpGrid import CombineData
from CreateTokens import generate_tokens
from SetUpGrid import SetUpRun
from SetUpGrid import RunInstance

import json
import os
import datetime
import numpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

from irods.session import iRODSSession
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta
from irods.access import iRODSAccess
from helperFunctions import *

#Connect to iRODS
print('Connect to iRODS')
host = os.environ['HOST']
port = os.environ['PORT']
user = os.environ['USER']
password = os.environ['PASSWORD']
zone = os.environ['ZONE']
share = os.environ['SHARE']

#Data location on scratch
dataDir = os.path.dirname(os.environ['DATAPATH'])
print('Input data is stored here: '+dataDir)
resultsDir = os.path.dirname(os.environ['DATAPATH']).replace('data_', 'results_')
ensure_dir(resultsDir)
print('Output data is stored here: '+resultsDir)
print

session = iRODSSession(host=host, port=port, user=user, password=password, zone=zone)
#Search for input data and store it in the folder where the figshare data is located
print('Download data from iRODS')
ATTR_NAME = 'DATATYPE'
ATTR_VALUE = 'PATHWAYS'
query = session.query(Collection.name, DataObject.name)
filteredQuery = query.filter(DataObjectMeta.name == ATTR_NAME).\
                          filter(DataObjectMeta.value == ATTR_VALUE)
iPaths = iParseQuery(filteredQuery)
print('Downloading: ')
print('\n'.join(iPaths))
iGetList(session, iPaths, dataDir)

#Create collection for ACES results
coll = session.collections.get('/' + zone + '/home/' +user)
collNames = [c.name for c in coll.subcollections]
resultsName = 'aces_results'
tmp = resultsName
count = 0
while resultsName in collNames:
        resultsName = tmp + '_' +str(count)
        count = count + 1
print('Upload results to: '+ coll.path + '/' + resultsName)
coll = session.collections.create(coll.path + '/' + resultsName)
print

# Calculate results
DataAndFeatureExtractors = CombineData()
for item in DataAndFeatureExtractors:
    tokens = generate_tokens([item], 1, 5, "PerfTest")
    (data, net, featureSelector, classifiers, Dataset2Time) = \
        SetUpRun(item[0], item[1][1], item[1][0][0], datafile = os.path.basename(os.environ['DATAPATH']), datapath=dataDir)
    for token in tokens:
        dataset = token['input']['dataset']
        network = token['input']['network']
        method = token['input']['method']
        repeat = token['input']['repeat']
        fold = token['input']['fold']
        print 'dataset:', dataset
        print 'network', network
        print 'method', method
        print 'repeat', repeat
        print 'fold', fold
        (dataName, featureExtractorproductName, netName, shuffle, featureExtractor, AucAndCi) = RunInstance(
                    data, net, featureSelector, None, classifiers, repeat, 5, fold, None, Dataset2Time, None)
        token['output'] = (dataName, featureExtractorproductName, netName, None, shuffle, featureExtractor, AucAndCi)

    # Store raw output data in iRODS
    try:
        filebase = item[0]+'_'+item[1][0][0]+'_'+item[1][1]
    except:
        filebase = item[0]+'_'+item[1][0][0]
    with open(resultsDir+'/'+filebase+'_raw.json', 'w') as outfile:
        json.dump(tokens, outfile)

    #upload raw data
    print('Write raw data to iRODS: '+ coll.path+'/'+filebase+'_raw.json')
    session.data_objects.put(resultsDir+'/'+filebase+'_raw.json', coll.path+'/'+filebase+'_raw.json')
    obj = session.data_objects.get(coll.path+'/'+filebase+'_raw.json')
    #Add metadata
    obj.metadata.add('ISEARCH', ATTR_NAME + '==' + ATTR_VALUE)
    obj.metadata.add('ISEARCHDATE', str(datetime.date.today()))
    obj.metadata.add('REFDATA', 'http://dx.doi.org/10.6084/m9.figshare.3119248.v1')
    obj.metadata.add('DATATYPE', 'ACES results')
    obj.metadata.add('ALGORITHM', filebase)

    # Create figures
    performance = []
    for token in tokens:
        performance.append([token['output'][6]['BinaryNearestMeanClassifier_V1'][perf][0] 
            for perf in token['output'][6]['BinaryNearestMeanClassifier_V1'].keys()[:50]])

    plt.plot(numpy.transpose(performance))
    plt.xlabel('Features')
    plt.ylabel('AUC (performance)')
    plt.title(token['output'][1]+' '+str(token['output'][2]))    
    figName = 'performance_'+filebase+'.png'
    plt.savefig(resultsDir+'/'+figName)
    plt.clf()
    # Upload to iRODS
    print('Write plot to iRODS: '+coll.path+'/'+figName)
    session.data_objects.put(resultsDir+'/'+figName, coll.path+'/'+figName)
    obj = session.data_objects.get(coll.path+'/'+figName)
    obj.metadata.add('REFDATA', 'http://dx.doi.org/10.6084/m9.figshare.3119248.v1')
    obj.metadata.add('DATATYPE', 'ACES results')
    obj.metadata.add('ALGORITHM', filebase)

    # Extract 50 most differentially expressed features
    bestFeatures = []
    for token in tokens:
        _, genes, features = json.loads((token['output'][5]))
        if item[1][1] != None:
            genelist = [genes[feat] for sublist in features[:10] for feat in sublist]
        else:
            genelist = features[:10]
        bestFeatures.append(genelist)
    csvName = 'features_'+filebase+'.csv'
    with open(resultsDir+'/'+csvName, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(bestFeatures)

    # Upload to iRODS
    print('Write feature csv to iRODS: '+coll.path+'/'+csvName)
    session.data_objects.put(resultsDir+'/'+csvName, coll.path+'/'+csvName)
    obj = session.data_objects.get(coll.path+'/'+csvName)
    obj.metadata.add('REFDATA', 'http://dx.doi.org/10.6084/m9.figshare.3119248.v1')
    obj.metadata.add('DATATYPE', 'ACES results')
    obj.metadata.add('ALGORITHM', filebase)

#Share results with user 
acl = iRODSAccess('read', coll.path, share, session.zone)
print('Share data: '+acl.access_name+' '+acl.user_name+' '+acl.path)
try:
    session.permissions.set(acl)
except:
    print("User or group unknown: "+share)

for srcColl, colls, objs in coll.walk():
    for obj in objs:
        try:
            acl = iRODSAccess('read', obj.path, share, session.zone)
            session.permissions.set(acl)
        except:
            print("User or group unknown: "+share)
