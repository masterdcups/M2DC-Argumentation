import pandas as pd
import json

def cleanDataframe(edges_df):
    """
    Prepare dataframe format, like
        - converting string to int
        - None to -1
        - Ex: for wikidebats: n1,n2-> int64
    If None exists = -1, for the root nodes with empty edge
    Returns edges Dataframe 
    """
    edges_df['n2'].replace('None',-1,inplace=True)
    edges_df = edges_df.astype({'n1':'int64', 'n2':'int64'})
    return edges_df


def getTopics(edges_df,nodes_df):
    """
    A topic considered as : a node with non connecting edges.
    With the previous definition we find them as : nodes(n2)-nodes(n1)
    Returns Dataframe of selected nodes
    """
    new_edges_df = edges_df[edges_df['n2']!=-1]
    tos, froms = set(new_edges_df['n2']), set(new_edges_df['n1'])
    topics_df = tos.difference(froms)
    return nodes_df[nodes_df['n'].isin(topics_df)][['n', 'label']]


def dfs(cur_node,edges_df, vis, nedges_df):
    """
    DFS to find the connected component of a given topic.
    Returns: set of visited nodes, edges list
    """
    vis.add(int(cur_node))
    for index,row in edges_df[edges_df['n2']==cur_node].iterrows():
        if row['n1'] not in vis:
            nedges_df.append([int(row['n1']), int(row['n2']), row['weight']])
            vis, nedges_df = dfs(row['n1'], edges_df, vis, nedges_df)
    return vis, nedges_df


#TODO save network.body.data.nodes._data
#TODO network.body.data.edges._data

def makeJson(nodes_df, edges_df, lnodes, ledges):
    """
    Prepare json file format for input JS library
    Returns: json object
    """
    nodes = []
    edges = []

    # iterates over dataframe to add nodes to JSON
    for index,row in nodes_df[nodes_df['n'].isin(lnodes)].iterrows():
        try:
            nodes.append({'id': row['n'], 'label': row['label'].replace("\'"," "), 'shape':'box'})
        except:
            nodes.append({'id': row['n'], 'label': row['url'], 'shape':'box'})
    
    # Templates for edges shape in graph
    pro = {
            'from':{
                'enabled':True,
                'type':'arrow'
                }
            }

    con ={ 
             'from':{
                'enabled':True,
                'type':'box'
                }
            }

    # iterates over edges to add edges to JSON
    for edge in ledges:
        if edge[2]>0:
            edges.append({ 'from': int(edge[1]), 'to': int(edge[0]), 'arrows': pro, 'color': {'color':'green'}  })
        else:
            edges.append({ 'from': int(edge[1]), 'to': int(edge[0]), 'arrows': con, 'color': {'color':'red'}  })

    tmp_json = {'nodes':nodes, 'edges':edges}
    json_txt = json.dumps(tmp_json)
    return json_txt
