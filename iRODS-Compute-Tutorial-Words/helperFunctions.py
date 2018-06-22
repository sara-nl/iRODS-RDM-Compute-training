"""
@licence: Apache 2.0
@Copyright (c) 2017, Christine Staiger (SURFsara)
@author: Christine Staiger
"""
import os

#wordcount
from collections import Counter
import json
import string

#irods
import irods.keywords as kw

#create directory if it does not exist already
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

#wordcount program
#simple wordcount function which counts every instance of a word, note case sensitive
def wordcount(dataFiles, resultsDir):
    print dataFiles
    print resultsDir
    words = []
    for path in dataFiles:
        with open(path) as f:
            text = f.read().split()
        newWords = [''.join(char for char in word
             if char not in string.punctuation) for word in text]
        words.extend(newWords)
    print len(words)

    numWords = Counter(words)

    #store results
    resultsFile=resultsDir+"/resultswordcount.dat"
    with open(resultsFile, 'w') as file:
        file.write(json.dumps(numWords))
    return resultsFile

#irods helper functions
def iParseQuery(queryResults):
    """
    Parse a query that fetched Collection.name and DataObject.name; the function creates the full iRODS path of all yielded files.

    Usage example:
    iParseQuery(sess.query(Collection.name, DataObject.name))
    iParseQuery(sess.query(Collection.name, DataObject.name).filter(DataObjectMeta.name == 'author' and DataObjectMeta.value == 'Lewis Carroll'))
    """
    iPaths = []
    results = queryResults.get_results()

    for item in results:
        for k in item.keys():
            if k.icat_key == 'DATA_NAME':
                name = item[k]
            elif k.icat_key == 'COLL_NAME':
                coll = item[k]
            else:
                continue
        iPaths.append(coll+'/'+name)
    return iPaths

def iGetList(sess, iPaths, destFolder):
    """
    Downloads a list of data objects from iRODS and saves them in the destination folder.
    Watch out: Data will be overwritten!
    Example usage:
    iGetList(sess, ['/aliceZone/home/irods-user1/myiPyFun.py'], '/home/user1/dataFilesToCompute')

    Parameters:
    sess    - iRODS session
    iPaths  - List of full iRODS paths to data objects
    destFolder - Location, unix filesystem
    """
    ensure_dir(destFolder)
    print "Write to: ", destFolder
    for iPath in iPaths:
        buff = sess.data_objects.open(iPath, 'r').read()
        with open(destFolder+'/'+os.path.basename(iPath), 'wb') as f:
            f.write(buff)

def iPutFile(sess, fileName, iPath):
    """
    Uploads a file to iRODS and returns the iRODS data object.
    Watch out: Returns an error if data object already exists.
    Example usage:
    myObj = iPutFile(sess, "/home/user1/pythonscripts/helperFunctions.py", "/aliceZone/home/irods-user1/myiPyFun.py")

    Parameters:
    sess    - iRODS session
    iPath   - Full iRODS paths to destination data object
    fileName - Full path to file, unix filesystem
    """

    options = {kw.REG_CHKSUM_KW: ''}

    with open(fileName, 'r') as f:
        content = f.read()

    obj = sess.data_objects.create(iPath)
    with obj.open('w', options) as obj_desc:
        obj_desc.write(content)

    obj = sess.data_objects.get(iPath)

    return obj

def iLsColl(sess, iPath):
    """
    Lists the whole iRODS collection recursively.
    Exanple usage:
    iLsColl(sess, '/aliceZone/home/irods-user1')

    Parameters:
    sess    - iRODS session
    iPath   - Full iRODS paths to the iRODS collection
    """

    iColl = sess.collections.get(iPath)
    for srcColl, subColls, objs in iColl.walk():
        print "-C "+srcColl.path
        print "\n".join(["    "+obj.path for obj in objs])

