import os
import datetime
from helperFunctions import *

from irods.session import iRODSSession
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta

#PARAMETERS
# iRODS connection
host='<iRODS host>'
port=1247
user='<your username>'
password='<your password>'
zone='aliceZone'

# data search
ATTR_NAME = 'author'
ATTR_VALUE = 'Lewis Carroll'

print('Creating directories for analysis and results')
dataDir = os.environ['TMPDIR']+'/wordcountData_'+user
ensure_dir(dataDir)
resultsDir = os.environ['TMPDIR']+'/wordcountResults_'+user
ensure_dir(resultsDir)

print('Connect to iRODS')
session = iRODSSession(host=host, port=port, user=user, password=password, zone=zone)

print('Searching for files')
query = session.query(Collection.name, DataObject.name)
filteredQuery = query.filter(DataObjectMeta.name == ATTR_NAME).\
                          filter(DataObjectMeta.value == ATTR_VALUE)
print filteredQuery.all()
iPaths = iParseQuery(filteredQuery)

print('Downloading: ')
print('\n'.join(iPaths))
iGetList(session, iPaths, dataDir)

print('Start wordcount')
dataFiles = [dataDir+'/'+f for f in os.listdir(dataDir)]
resFile = wordcount(dataFiles,resultsDir)

#upload
coll = session.collections.get('/' + zone + '/home/' +user)
objNames = [obj.name for obj in coll.data_objects]
f = os.path.basename(resFile)
count = 0
while f in objNames:
        f = os.path.basename(resFile) + '_' +str(count)
        count = count + 1

print('Upload results to: ', coll.path + '/' + f)
session.data_objects.put(resFile, coll.path + '/' + f)

print('Adding metadata')
obj = session.data_objects.get(coll.path + '/' + f)
for iPath in iPaths:
        obj.metadata.add('INPUTDAT', iPath)

obj.metadata.add('ISEARCH', ATTR_NAME + '==' + ATTR_VALUE)
obj.metadata.add('ISEARCHDATE', str(datetime.date.today()))

print('Metadata for: ', coll.path + '/' + f)
print('\n'.join([item.name +' \t'+ item.value for item in obj.metadata.items()]))
