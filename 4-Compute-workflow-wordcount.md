<img align="right" src="surfsara.png" width="100px">
<br><br>

# Data management and compute

**Authors**
- Arthur Newton (SURFsara)
- Christine Staiger (SURFsara)

**License**
Copyright 2018 SURFsara BV

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Goal

In this module you will learn how to interact with the iRODS platform from an HPC cluster and from within a compute workflow.
You will:

- Write a compute workflow drawing on data in iRODS (search and download).
- Write result data back to iRODS.
- Introducing provenance metadata to results.
- Submit the workflow to the scheduling system of the HPC cluster.

## Course material

We prepared some parts of the workflow for you. Please download the code with:

```sh
git clone https://github.com/sara-nl/RDM-Compute-training.git
cd RDM-Compute-training/iRODS-Compute-Tutorial-Words/

ipython
```

## Data on an HPC cluster
On most HPC clusters you have access to different file systems which come with different advantages and disadvantages. 

- Your **home** folder lies on a file system which is mounted to all nodes in the compute cluster, i.e. all data which is stored there is accessible and writable from all worker and data nodes. However, the quota on that files system per user is normally very restructed and the data access is slower.
- If you need to store larger data or data which need to be accessed fast during the computation you would use the **scratch** file system. Each node in the compute cluster has its own **scratch space**. It is thus not shared between nodes and you need to make sure that data is stored there before you access it from your compute workflow.

You can get the path to your **home** folder from python with:

```py
import os
os.environ['HOME']
```

Or **scratch space** with:

```py
os.environ['TMPDIR']
```

## Compute workflow - Wordcount
We will now prepare the compute workflow as it should be executed on any worker node in the cluster. We still do that in interactive mode and on the user interface node (remember it behaves as any node in the cluster).

### Create data folders on **scratch**

```py
import os
from helperFunctions import *

print('Creating directories for analysis and results')
dataDir = os.environ['TMPDIR']+'/wordcountData' + '<your id>'
ensure_dir(dataDir)
print(dataDir)
resultsDir = os.environ['TMPDIR']+'/wordcountResults' + '<your id>'
ensure_dir(resultsDir)
print(resultsDir)
```

### Connecting to iRODS

```py
import getpass
pw = getpass.getpass().encode('base64')
```

```py
from irods.session import iRODSSession
session = iRODSSession(host='sara-alice.grid.surfsara.nl', port=1247, user='irods-user1', password=pw.decode('base64'), zone='aliceZone')
```

### Searching for files

```py
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta

print('Searching for files')
ATTR_NAME = 'author'
ATTR_VALUE = 'Lewis Carroll'

query = session.query(Collection.name, DataObject.name)
filteredQuery = query.filter(DataObjectMeta.name == ATTR_NAME).\
                          filter(DataObjectMeta.value == ATTR_VALUE)
print(filteredQuery.all())
iPaths = iParseQuery(filteredQuery)
```

### Downloading files from iRODS to **scratch**
Remember from the first part of the tutorial, that for downloading data from iRODS you first have to read the data object into memory and after that write it to a file on your local filesystem. For convenience we provide a function wich does that for us for a list of data objects.

```py
print('Downloading: ')
print('\n'.join(iPaths))
iGetList(session, iPaths, dataDir)
```

### Execute compute workflow
Now we can finally do our analysis:

```py
dataFiles = [dataDir+'/'+f for f in os.listdir(dataDir)]
resFile = wordcount(dataFiles,resultsDir)
```

### Upload results to iRODS

```py
#Check if results are actually created and ingested into iRODS
coll = session.collections.get('/aliceZone/home/irods-user1')
objNames = [obj.name for obj in coll.data_objects]
f = os.path.basename(resFile)
count = 0

while f in objNames:
    f = os.path.basename(resFile) + '_' +str(count)
    count = count + 1

#upload
print('Upload results to: ', coll.path + '/' + f)
session.data_objects.put(resFile, coll.path + '/' + f)
```

### Introduce some metadata for provenance

```py
import datetime
```

```py
obj = session.data_objects.get(coll.path + '/' + f)
for iPath in iPaths:
    obj.metadata.add('INPUTDAT', iPath)

obj.metadata.add('ISEARCH', ATTR_NAME + '==' + ATTR_VALUE)
obj.metadata.add('ISEARCHDATE', str(datetime.date.today()))
print('\n'.join([item.name +' \t'+ item.value for item in obj.metadata.items()]))
```

## Running the python workflow
Now we transfer the workflow to a python script. Exit ipython.
We prepared the whole workflow for you. Inspect the file *wordsWorkflow.py* and adjust the parameters:

```sh
vi wordsWorkflow.py
#PARAMETERS
# iRODS connection
host='sara-alice.grid.surfsara.nl'
port=1247
user='irods-user1'
password='<your password>'
zone='aliceZone'
```

```sh
python wordsWorkflow.py
```

## Submit the workflow to the scheduler
Open the file 'words_jobscript' and adjust your user name and path in the line:

```sh
cd /home/<user>/../iRODS-Compute-Tutorial-Words
```

Now you can submit the job to the queue:

```sh
sbatch jobscript
squeue -u <username>
```
If the job finished successfully the file *jobscript.e...* will be empty, everything which our python scripts gives as output is saved in *outputjob*.
Now we can check with a graphical user interface whether the data is really there.
