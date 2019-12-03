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

## GOAL

In this module we will run a more complex workflow and save results of the compute worflow during their calculations and link them through metadata.

## Workflow description
ACES is a software package that finds and defines feature for classification of cancer patients. 
It uses as input data some gene expression data and as parameters gene interaction network data. 
It defines differentially expressed genes and aggregation of genes.

- Download some published data from a repository (FigShare). 
This data will serve as input data.
- Search in the iRODS instance for some additional data. 
We prepared some biological gene network data in the iRODS instance which the pipeline takes as parameter.
- The code will execute a five-fold cross validtaion
- Results: a ranking of the features and performances measured in Area under the receiver operator curve (AUC)

The results and intermediate results are stored immediately in iRODS while the pipeline continues running.
In the end the results are opened for read access to another user.

## Code

```sh
/home/<path>/iRODS-Compute-Tutorial-ACES
```
Inspect the workflow in `acesWorkflow.py`.

We see that the pipeline reads in some environment variables which need to be defined in the jobscript.

Adjust all parameters in the jobscript `jobscript_aces`:

```sh
#!/bin/bash
#Set job requirements
#SBATCH -N 1
#SBATCH -t 15:00

#iRODS + Python
module load pre2019
module load icommands
module load Python
cd /home/<FILL IN>/iRODS-Compute-Tutorial-ACES

#parameters for iRODS connection
export HOST=<FILL IN>
export PORT=1247
export USER=<FILL IN>
export PASSWORD=<FILL IN>
export ZONE=<FILL IN>

#iRODS user to share results with
export SHARE=<FILL IN>

#download reference data
wget -P $TMPDIR/<FILL IN> https://ndownloader.figshare.com/files/4851460
export DATAPATH=$TMPDIR/<FILL IN>/4851460

# call the program
python acesWorkflow.py > /home/<FILL IN>/iRODS-Compute-Tutorial-ACES/outputjob_aces
```

Start the workflow and verify with your neighbour that results are shared.
