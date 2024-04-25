import numpy as np
import sys
import csv
import pygraphviz as pgv
import entropy as en
import pickle


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

# Get edges from dot file
def getedgefromdot(dotfile):
    G=pgv.AGraph(dotfile)
    nodes=np.sort(np.array(G.nodes()))
    edges=np.array([e[0]+'->'+e[1] for e in  np.array(G.edges())])
    return edges

# create library(dictionary) for labels(nodes)
def getlabdict(nodes):
    labdict={}
    for index,element in enumerate(nodes):
        labdict[element]=index
    return labdict

# Create enumerated edges array
def edgeenumerate(edgenames,labdict):
    edgesplit=np.array([i.split('->') for i in edgenames])
    return np.array([[labdict[i],labdict[j]] for i,j in edgesplit])

# Compute MI for all edges in given interval w
def intervalMI(data,edgenums,w):
    return [en.mi_p([data[i][w[0]:w[1]],data[j][w[0]:w[1]]]) for i,j in edgenums]


def changeedgelabels(graph,scores):
    E=graph.edges()
    for i,j in enumerate(E):
        graph.get_edge(j[0],j[1]).attr['label']=scores[i]

def graphtopickle(graph,outfile):
    with open (outfile, 'wb') as f:
        pickle.dump(graph,f)


class Rescore():
   
    def __init__(self,dotfile,datacsv,intervals):
        self.dotfile=dotfile
        self.intervals=intervals
        self.datacsv=datareader(datacsv)
        self.data=self.datacsv[1:,:].astype(int)
        self.labels=self.datacsv[0]
        self.dirout=('./')
        self.edges=getedgefromdot(dotfile)#./rendering.dot')

    def runintervals(self):
        edgenums=edgeenumerate(self.edges,getlabdict(self.labels))
        self.scores=[]
        for i in self.intervals:
            scores=intervalMI(self.data.T,edgenums,i)
            self.scores.append(scores)

    def outputs(self,writedot=False):
        sources=np.array([i.split('->') for i in self.edges])[:,0]
        targets=np.array([i.split('->') for i in self.edges])[:,1]
        labels=np.array(['source','target','weight'])
        self.outarr=[]
        G=pgv.AGraph(self.dotfile)
        for j,i in enumerate(self.intervals):
            scores=np.array(self.scores[j]).astype(float)
            outarr=np.column_stack((sources,targets,scores))
            self.outarr.append(outarr)
            datawrite(f'./intv{j+1}_{i[0]}-{i[1]}.csv',outarr,labels)
            if writedot==True:
                cG=G
                changeedgelabels(cG,self.scores[j])
                cG.write(f'./intv{j+1}_{i[0]}-{i[1]}.dot')
                
                
            

