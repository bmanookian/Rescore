import numpy as np 
import pygraphviz as pgv
import subprocess
import igraph as ig
import sys
#path to your bnomics folder
sys.path.append('/home/bmanookian/bnomics/')
import bnomics as bn




def load_dot(input_file):
    agraph = pgv.AGraph(input_file)
    return agraph

def fix_position(input_file):
    # Run the dot command
    output_file='.'.join(input_file.split('.')[:-1])+'_pos_fixed.dot'
    #print(output_file)
    command = ["dot", "-Tdot", input_file, "-o", output_file]
    subprocess.run(command, check=True)
    return output_file

def convert_to_igraph(f,directed=True):
    """
        f=file do a grah in dot format

        return the file in igraph format where only the topology is retained
            
    """

    pgv_graph=f
    if type(pgv_graph)==str:
        pgv_graph=load_dot(pgv_graph)
        
    # Create an empty igraph graph
    igraph_graph = ig.Graph(directed=directed)

    # Add nodes to the igraph graph
    for node in pgv_graph.nodes():
        igraph_graph.add_vertex(name=node)

    # Add edges to the igraph graph
    for edge in pgv_graph.edges():
        source_node = edge[0]
        target_node = edge[1]
        igraph_graph.add_edge(source_node, target_node)

    return igraph_graph


def loadData(dt):
    #if dt[-3:]=='npy':
    #    dt=np.load(dt)
    dt=bn.dutils.loader(dt)
    return dt



def allignAdj(f,g,ofunc=bn.cmu,bins=3,directed=True):
    """
        f is the file address,a numpy table or dutils.dataset with data to score.
        g is igraph object or a file address to a dot file 
    """
    dt=f
    #if type(dt)==str:
    dt=loadData(dt)
    
    if type(g)==str:
        g=convert_to_igraph(g,directed=directed)
    dt.quantize_all(bins=bins)
    srch=bn.search(dt, ofunc=ofunc)
    lab=np.array(srch.variables)
    nodeMap=dict(zip( np.arange(len(g.vs)),[np.where(lab==x)[0][0] for x in g.vs['name']] ))
    structure = srch.BN
    #return srch,nodeMap
    for edge in g.es:
         #print(g.vs['name'][edge.source],g.vs['name'][edge.target])
         #print(lab[nodeMap[edge.source]],lab[nodeMap[edge.target]])
         #print('___\n')
         structure.add_edge(nodeMap[edge.target],nodeMap[edge.source])
    #srch.BN = deepcopy(structure)
    srch.score_net()
    return srch
                
def scoreEdges(srch):
    node_index=srch.node_index
    BN=srch.BN
    ind_map=[BN.node_names.index(i) for i in BN.node_names]
    s=[]
    for cnode in node_index:
        for pnode in BN.pnodes[cnode]:
                # In case BN is a Markov Neighborhood translate the edge
                # indices into their global equivalent and score. Otherwise the
                # map is an identity
            cnode_g=ind_map[cnode]
            pnode_g=ind_map[pnode]
            edge_score=srch.score_edge(cnode_g,pnode_g)
            s.append([BN.node_names[pnode],BN.node_names[cnode],edge_score])
    return s

def diffGraph_pw_pgv(g1,g2,directed=True,fileOut=None,colorMap=color_bi_linear):
    "it assume g1,g2 have been scored and have exactly the same topology"
        
    if type(g1)==str:
        g1=load_dot(g,directed=directed)
    if type(g2)==str:
        g2=load_dot(g,directed=directed)
    
    dg=g1.copy()
    min_dif=0
    max_dif=0
    for edge1 in g1.edges_iter():
        edge2=g2.get_edge(*edge1)
        edgeDg=dg.get_edge(*edge1)
        e1=float(edge1.attr['label'])
        e2=float(edge2.attr['label'])
        de=edgeDiff(e1,e2)
        edgeDg.attr['label']=de
        if np.isfinite(de):
            if de<min_dif:
                min_dif=de
            if de>max_dif:
                max_dif=de
    return dg


def projectData_pw(dt,fG,bins=8,directed=True,ofunc=bn.cmu,fileOut=False):
    """
        fG has to be a pointer to a dt file with position fixed
    """

    if type(dt)==str:
        dt=loadData(dt)
    G=convert_to_igraph(fG,directed=directed)
    srch=allignAdj(dt,G,ofunc=ofunc,bins=bins,directed=directed)

    #WE NEED TO DO EVERITHING IN PGV!
    G=load_dot(fG)
    g=G.copy()
    srch.score_edges()
    edge_scores=srch.edge_scores
    pnode=srch.BN.pnodes
    variables=srch.variables
    #return g,pnode,srch,edge_scores
    for i,pp in enumerate(pnode):
        for j,p in enumerate(pp):
            edge=g.get_edge(variables[p],variables[i]) 
            edge.attr['label']=edge_scores[i][j]
    fileOut_dg=fileOut
    dg=diffGraph_pw_pgv(G,g,fileOut=None)
    return g,dg

def projectData_and_diff(dt1,fG,dirout=None,name1=None,bins=2,dictOut=None,dictDiff=None,directed=True,ofunc=bn.cmu,is_G_fixed=True):
     #print(bins)
     if not is_G_fixed:
        fG=fix_position(fG)
     #print('test')
     #fileOut1=dirout+name1
     g,dg=projectData_pw(dt1,fG,bins=bins,directed=directed,ofunc=ofunc,fileOut=None)
     if dictOut is None:
        dictOut={}
        dictDiff={}
     for edge in g.edges_iter():
        dictOut['->'.join(edge)]=edge.attr['label']
     for edge in dg.edges_iter():
        dictDiff['->'.join(edge)]=edge.attr['label']

     return dictOut,dictDiff
    


