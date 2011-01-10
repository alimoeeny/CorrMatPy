from numpy import zeros, array, loads as numpyLoads
from scipy.stats import pearsonr
from socket import MSG_WAITALL
from ANSIColors import *
from scipy.io import savemat, loadmat
from time import sleep, time
from random import randint

# number of cores
#cpucount = 4;

# Number of Neuron Pools ( 8 for 0, 45, 90, 135, 180, 270, 315) 
PoolCount = 5; #8;

# Neurons in each of 8 pulls
nn = 1000; #100

#total number of neurons
Nn = PoolCount * nn;

# number of trials
Tn = 100; # 1000;

# Population Average firing rate to initialize with
PopmFr = 1;

# # Target Correlation Matrix
### --- 8 pools with only one within pool corr value and only one between pool corr value 
# CorrMat = zeros((Nn, Nn))+0.1;
# for pool in range(0, PoolCount):
#     CorrMat[pool*nn:pool*nn+nn,pool*nn:pool*nn+nn] = 0.2;

# for i in range(0, Nn):
#     CorrMat[i, i] = 1;

### --- 8 pools with only one within pool corr value and LINEARLY GRADED between pool corr values 
# corrWithin = 0.3
# corrMinBetween = 0.1
# CorrMat = zeros((Nn, Nn)) + corrMinBetween;
# for pool in range(0, PoolCount):
#     for offset in range(0, PoolCount):
#          CorrMat[pool*nn:pool*nn+nn, (offset)*nn:(offset)*nn+nn] = corrWithin - (1.0*abs(-pool + offset)/(PoolCount-1) * (corrWithin - corrMinBetween));

# for i in range(0, Nn):
#     CorrMat[i, i] = 1;

### --- 7 pools with only one within pool corr value and LINEARLY GRADED correlations up to orthogonal and then FLAT after that 
PoolCountHalf = 4;

corrWithin = 0.2
corrMinBetween = 0.1
CorrMat = zeros((Nn, Nn)) + corrMinBetween;

for pool in range(0, PoolCount):
    for offset in range(0, PoolCount):
        if (((pool > 3) | (offset > 3)) & (pool<> offset)):
            CorrMat[pool*nn:pool*nn+nn, (offset)*nn:(offset)*nn+nn] = corrMinBetween;
        else:
            CorrMat[pool*nn:pool*nn+nn, (offset)*nn:(offset)*nn+nn] = corrWithin - (1.0*abs(-pool + offset)/(PoolCountHalf-1) * (corrWithin - corrMinBetween));

for i in range(0, Nn):
    CorrMat[i, i] = 1;


### --- Flat Corr Matrix
#CorrMat = zeros((Nn, Nn))+0.1;
#for i in range(0, Nn):
#    CorrMat[i, i] = 1;




# Number of itteration toward a local optimum
AllowedIt = 10;

# Minimal Accpetable Correlation difference
MACD = 0.008;

# k
k = 1;

BUFF_SIZE = 32768;

#HOST = "10.1.0.2"
#HOST="localhost"
PORT = 9966


def logIt(s):
    f = open('CorrMat.log', 'a');
    f.write(s);
    f.close();
