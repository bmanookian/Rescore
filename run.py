import numpy as np
import sys
sys.path.append('/home/bmanookian/Rescore/')
import rescore as rs

### INTERVALS ###

# Input the intervals for which you would like to rescore with
# change the variable accordingly for desired number of intervals

intervals=[[0,300],[300,500],[500,700]]

### 



# Data file (csv) and universal BN dotfile inputs

datafile=sys.argv[0]
dotfile=sys.argv[1]

R=rs.Rescore(dotfile=dotfile,datacsv=datafile,intervals=intervals)


# Here will be lines of code for checking for single states in intervals
R.checksingles()
R.temp()



## Rescoring
    ### NOTE: Only one runinterval should be run before output generation

# This will run the rescoring for given intervals
R.runintervals_temp()


# The below line of code will run intervals without any alterations
# R.runintervals()


# Output generation
# Create an output csv for each interval and corresponding scores and diffs
R.outputs()
