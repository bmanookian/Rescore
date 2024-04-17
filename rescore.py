import numpy as np
import sys
import csv
sys.path.append('/home/bmanookian/python_codes/')
import diffgraph as dg



def datareader(inputfile):
    out = []
    with open(inputfile, newline = '') as file:
        reader = csv.reader(file)
        for i,row in enumerate(reader):
            out.append(row)
    return np.array(out)

def datawrite(output,data,labels=None):
    with open(output, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if labels is not None:
            csv_writer.writerow(labels)
        for row in data:
            csv_writer.writerow(row)


def chkone(data,v,interval):
    return np.all(data[:,v][interval[0]:interval[1]].astype(bool))

def chkzero(data,v,interval):
    return np.all(~data[:,v][interval[0]:interval[1]].astype(bool))

def changelastvalue(data,v,interval):
    if data[:,v][interval[0]:interval[1]][-1]==1:
        data[:,v][interval[0]:interval[1]][-1]=0
    else:
        data[:,v][interval[0]:interval[1]][-1]=1 
    return data

class Rescore():
   
    def __init__(self,dotfile,datacsv,intervals):
        self.dotfile=dotfile
        self.intervals=intervals
        self.datacsv=datareader(datacsv)
        self.data=self.datacsv[1:,:].astype(int)
        self.labels=self.datacsv[0]
        self.dirout=('./')
        self.labs=self.labels.shape[0]


    def checksingles(self):
        self.singles=[]
        for i in self.intervals:
            t1=[chkone(self.data,v,i) for v in range(self.labs)]
            t0=[chkzero(self.data,v,i) for v in range(self.labs)]
            self.singles.append(np.where(np.array([np.any(t) for t in np.column_stack((t1,t0))])==True)[0])
        return

    def temp(self):
        self.tempdata=np.copy(self.data)
        for j,i in enumerate(self.intervals):
            for k in self.singles[j]:
                self.tempdata=changelastvalue(self.tempdata,k,i)       
        

    def runintervals_temp(self):
        self.scoredicts=[]
        self.diffdicts=[]
        for j,i in enumerate(self.intervals):
            out_dict,diff_dict=dg.projectData_and_diff(
                np.vstack((self.labels,self.tempdata[i[0]:i[1],:])),
                self.dotfile,bins=2,is_G_fixed=False
                )
            self.scoredicts.append(out_dict)
            self.diffdicts.append(diff_dict)
        self.edges=list(self.scoredicts[0].keys())


    def runintervals(self):
        self.scoredicts=[]
        self.diffdicts=[]
        for i in self.intervals:
            out_dict,diff_dict=dg.projectData_and_diff(
            np.vstack((self.labels,self.data[i[0]:i[1],:])),
            self.dotfile,bins=2,is_G_fixed=False
            )
            self.scoredicts.append(out_dict)
            self.diffdicts.append(diff_dict)
        self.edges=list(scoredicts[0].keys())

    def outputs(self):
        sources=np.array([i.split('->') for i in self.edges])[:,0]
        targets=np.array([i.split('->') for i in self.edges])[:,1]
        labels=np.array(['source','target','scores','diff'])
        self.outarr=[]
        for j,i in enumerate(self.intervals):
            scores=np.array(list(self.scoredicts[j].values())).astype(float)
            diffs=np.array(list(self.diffdicts[j].values())).astype(float)*-1
            outarr=np.column_stack((sources,targets,scores,diffs))
            self.outarr.append(outarr)
            datawrite(f'./interval{j+1}_{i[0]}-{i[1]}.csv',outarr,labels)
            

