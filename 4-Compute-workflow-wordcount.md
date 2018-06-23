
Inspect the workflow in ``

Adjust all parameters in the job file

```sh
#iRODS + Python
module load icommands
module load python/2.7.9
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
python acesWorkflow.py > outputjob_aces
```
