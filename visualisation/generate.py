import os, sys
import json
import pandas as pd
from utils import *


def prepareGraph(nodes_df, edges_df, path):
    """ 
    Prepare topics list and json graphs for the JS lib 
    Returns: df_topics, json_topics: dict 'id_topic'->json_graph
    """
    edges_df = cleanDataframe(edges_df)
    df_topics = getTopics(edges_df, nodes_df)
    print(df_topics) 

    with open(path+"/listTopics.csv", "w") as outfile:
        for index,row in df_topics.iterrows():
            outfile.write(str(row['n'])+"\t"+str(row['label'])+"\n")
        
    print(len(df_topics), "topics found. Stored in ", path)
    for index,row in df_topics.iterrows():

        lnodes, ledges = dfs(row['n'], edges_df, set(), []) 
        json_txt = makeJson(nodes_df, edges_df, lnodes, ledges)

        with open(path+"/"+str(row['n']), 'w') as outfile:
            json.dump(json_txt, outfile)
        #json_topics[row['n']] = json_txt

    return None

def main():
    sources = ["wd", "kl", "am-fr"]
    name_s = ["Wikidebat","Kialo","Arguman-Fr"]
    for source,name in zip(sources,name_s):
        # create path to store json
        path = "json/"+source
        try:
            os.mkdir(path)
        except:
            print("Path already exists or error in creation")

        #read csv source files
        nodes_df = pd.read_csv("data/"+source+"_nodes.csv", sep=",")
        edges_df = pd.read_csv("data/"+source+"_edges.csv", sep=",")

        #generate and save jsons
        prepareGraph(nodes_df, edges_df, path)

if __name__=="__main__":
    main()

