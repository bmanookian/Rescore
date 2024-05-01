import numpy as np
import sys
sys.path.append('/home/bmanookian/Rescore/')
import rescore as rs

### INTERVALS ####

# Input the intervals for which you would like to rescore with
# change the variable accordingly for desired number of intervals

intervals=[[0,300],[300,500],[500,700]]

### 
# TO RUN

# Run this python file (run.py) with Data file (csv) and universal BN dotfile as inputs
###


###
datafile=sys.argv[1]
dotfile=sys.argv[2]

R=rs.Rescore(dotfile=dotfile,datacsv=datafile,intervals=intervals)

## Rescoring

R.runintervals()

# Output generation
# Create an output csv for each interval and corresponding scores
# If writedot is changed to true then a dot file will be produced for each interval
R.outputs(writedot=False)
