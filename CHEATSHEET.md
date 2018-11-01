<img align="left" src="surfresearchbootcamp_logo.png" width="500px">
<img align="right" src="surfsara.png" width="100px">
<br><br>

# The python API for iRODS - Cheat Sheet

**Authors**
- Arthur Newton (SURFsara)
- Christine Staiger (SURFsara)

**License**
Copyright 2018 SURFsara BV

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


## Connect to iRODS
```
from irods.session import iRODSSession
session = iRODSSession(host='sara-alice.grid.surfsara.nl', 
		   port=1247, user='irods-user1', password='yourpassword', 
		   zone='aliceZone')
```
 
## Data objects

Command 	| Meaning
---------|--------
session.data_objects.put(iPath, file)	| Put data in iRODS
session.data_objects.get(iPath)		| Load data object in memory
session.data_objects.move(currentPath, newPath) | Rename or move data object
**obj.metadata**	| **Operations for user defined metadata** 
obj.metadata.items()		| 
obj.metadata.keys() | 
obj.metadata.add(a, v, u) | 
obj.metadata.remove(a, v, u) |
session.data_objects.open(obj.path, 'r').read() | Read bitstream into memory

The object carries some vital system information. 

```
obj = session.data_objects.get(iPath)
obj.path
obj.name
obj.owner_name
obj.size
obj.checksum
obj.create_time
obj.modify_time
obj.metadata.items()
```

## iRODS collections
Command 	| Meaning
---------|--------
session.collections.create(iPath)	| Create collection
session.collections.get(iPath)		| Load collection in memory
session.collections.move(currentPath, newPath) | Rename or move collection (recursive by default)
**coll.metadata**	| **Operations for user defined metadata** 
coll.metadata.items()		| 
coll.metadata.keys() | 
coll.metadata.add(a, v, u) | 
coll.metadata.remove(a, v, u) |
coll.remove(recurse=True) | Remove collection and all its content

System information and content of a colection.

```py
coll = session.collections.get(iPath)
coll.path
coll.name
coll.subcollections
coll.data_objects
```

### Upload collection

```py
import os
dPath = os.environ['HOME'] + '/aliceInWonderland'
walk = [dPath]
while len(walk) > 0:
	for srcDir, dirs, files in os.walk(walk.pop()):
		print srcDir, dirs, files
		walk.extend(dirs)
   		iPath = iHome + srcDir.split(os.environ['HOME'])[1]
   		print "CREATE", iPath
   		newColl = session.collections.create(iPath)
   		for fname in files:
			print "CREATE", newColl.path+'/'+fname
      		session.data_objects.put(srcDir+'/'+fname, newColl.path+'/'+fname)
```

### Iterate over collection

```sh
for srcColl, colls, objs in coll.walk():
	print 'C-', srcColl.path
	for o in objs:
		print o.name
```

## Sharing data
Command 	| Meaning
---------|--------
session.permissions.get(\<coll or obj\>)	| Get all ACLs for a collection or data object
session.permissions.set(acl)		| Set ACLs of a collection or data object

```py
from irods.access import iRODSAccess
acl = iRODSAccess(KW, <coll.path or obj.path>, <group or user>, session.zone)
session.permissions.set(acl)
session.permissions.get(coll)
```
KW can take the values "read", "write", "own" or "null"


## Searching for data in iRODS
Example:

```py
query = session.query(Collection.name, 
					  DataObject.name, 
					  DataObject.checksum, 
					  DataObject.size, 
					  DataObjectMeta.value)
					  
filteredQuery = query.filter(DataObjectMeta.name == 'author').\
						  filter(DataObjectMeta.value == 'Lewis Carroll')
print filteredQuery.all()
```

### Parsing the iquest output
To work with the results of the query, we need to get them in an iterable format:

```py
results = filteredQuery.get_results()
```
**Watch out**: *results* is a generator which you can only use once to iterate over.

We can now iterate over the results and build our iRODS paths (*COLL_NAME/DATA_NAME*) of the data files:

```py
iPaths = []

for item in results:
    for k in item.keys():
        if k.icat_key == 'DATA_NAME':
            name = item[k]
        elif k.icat_key == 'COLL_NAME':
            coll = item[k]
        else:
            continue
    iPaths.append(coll+'/'+name)
print '\n'.join(iPaths)
```
