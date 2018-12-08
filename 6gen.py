import sys
import os
import datetime
from copy import deepcopy
clusterList =[]
'''
Cluster Range Function
'''
def updateClusterRange(oldRange,newRange):
    if(oldRange==""):
        return newRange
    newRange = list(newRange)
    for num in range(32):
        if(oldRange[num] != newRange[num]):
            newRange[num]='?'
    return ''.join(newRange)
def isClusterRange(seed,clusterRange):
    for num in range(32):
        if(clusterRange[num]=='?'):
            continue
        if(seed[num]!=clusterRange[num]):
            return False
    return True
def getClusterDistance(seed,cluster):
    count =0
    for num in range(32):
        if(cluster.range[num] == '?'):
            continue
        if(cluster.range[num] != seed[num]):
            count+=1
    return count

class Cluster(object):
    range = ''
    rangeSize =0
    seedSet=[]
    def __init__(self):
        self.range = ''
        self.rangeSize =0
        self.seedSet=[]
    def addSeedUpdateRange(self,seed):
        if seed in self.seedSet:
            return
        self.seedSet.append(seed)
        #update
        if(self.range==""):
            self.range = seed
        self.rangeSize =0 # init
        rangeList = list(self.range)
        for num in range(32):           
            if(rangeList[num]=="?"):
                self.rangeSize += 1# size +1
                continue
            if(rangeList[num] != seed[num]):
                rangeList[num]='?'
                self.rangeSize += 1# size +1
        self.range = ''.join(rangeList)
        #print "upate seed:"+str(seed)+"\n"+str(self.range)+"\n"+str(self.rangeSize)+"\n"

def InitClusters(seedList):
    for seed in seedList:
        cluster = Cluster()
        cluster.addSeedUpdateRange(seed)
        clusterList.append(cluster)
#Computes the minimum Hamming distance between cluster.range and
#all seeds in seedList not already in cluster , and returns the list
#of seeds that are this minimum distance away
def FindCandidateSeeds(cluster,seedList):
    minRangeSize = float('inf')
    seeds=[]
    for seed in seedList:
        if seed in cluster.seedSet:
            continue
        num =getClusterDistance(seed,cluster)
        if num < minRangeSize:
            minRangeSize =num
            seeds= []
            seeds.append(seed)  
        elif num == minRangeSize:
            seeds.append(seed)
    return seeds
#Consider growing all clusters by candidate seeds, 
# and select the growth resulting in the highest seed density 
# and smallest cluster range size
def GrowCluster(seedList):
    maxDensity = 0
    maxIndex = 0
    maxRangeSize = float('inf')#Inf inity
    maxCluster = None
    for index in range(0,len(clusterList)-1):         
        cluster = clusterList[index]
        candidateSeeds = FindCandidateSeeds(cluster,seedList)
        #if len(candidateSeeds)==0:
         #   return -1,None
        for seed in candidateSeeds:
            tmpCluster = deepcopy(cluster)#copy
            tmpCluster.addSeedUpdateRange(seed)
            for otherSeed in candidateSeeds:
                if isClusterRange(otherSeed,tmpCluster.range):#
                    tmpCluster.addSeedUpdateRange(otherSeed)
                    #
            if(tmpCluster.rangeSize!=0):
                newDensity = len(tmpCluster.seedSet)/tmpCluster.rangeSize
            else:
                newDensity =0
            if(newDensity > maxDensity or (newDensity==maxDensity and tmpCluster.rangeSize<maxRangeSize)):
                maxDensity = newDensity
                maxIndex = index
                maxRangeSize = tmpCluster.rangeSize
                maxCluster = tmpCluster
    return maxIndex,maxCluster 
#Grow clusters until the sum of cluster range sizes exceeds the budget. 
# For simplicity, we elide here details about handling cluster overlap
#and final cluster growth sampling to use up the budget exactly
def Ipv6Gen(seedList,budgetLimit):
    InitClusters(seedList)
    budgetUsed = 0
    while True:
        growIndex,growCluster = GrowCluster(seedList)
        oldRangeSize = clusterList[growIndex].rangeSize
        newRangeSize = growCluster.rangeSize
        budgetCost = newRangeSize -oldRangeSize
        budgetUsed = budgetUsed + budgetCost
        if((budgetUsed<=budgetLimit) and (len(seedList)>len(growCluster.seedSet))):
            clusterList[growIndex] = growCluster
        else:
            return clusterList
if __name__ == "__main__":
    seedList = []
    budgetLimit =100
    input = open(os.path.abspath(os.path.dirname(__file__))+"\ips.txt","r")
    while True:
        ipv6 = input.readline()
        if not ipv6:
            break
        seedList.append(ipv6)
    input.close()
    start = datetime.datetime.now()
    clusterList = Ipv6Gen(seedList,budgetLimit)
    end = datetime.datetime.now()
    
    num = 0
    qu = []
    out = open(os.path.abspath(os.path.dirname(__file__))+"\\result.txt","w")
    for cluster in clusterList:
        if len(cluster.seedSet) <=1:
            continue
        if cluster.range in qu:
            continue
        qu.append(cluster.range)
        num +=1
        print "Cluster "+str(num)+":"
        print cluster.range
        out.write(cluster.range)
    out.close()
    print "time cost:"+str(end-start)
        
