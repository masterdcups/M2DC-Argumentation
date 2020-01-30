import json

import pandas as pd
from flask import Flask, request, render_template
from utils import *

def prepareGraph(nodes_df, edges_df):
    """ 
    Prepare topics list and json graphs for the JS lib 
    Returns: df_topics, json_topics: dict 'id_topic'->json_graph
    """
    edges_df = cleanDataframe(edges_df)
    df_topics = getTopics(edges_df, nodes_df)
    print(df_topics)
    json_topics = {}
    for index,row in df_topics.iterrows():

        lnodes, ledges = dfs(row['n'], edges_df, set(), [])
        
        json_txt = makeJson(nodes_df, edges_df, lnodes, ledges)
        json_topics[row['n']] = json_txt

    return df_topics, json_topics

# Serve the file over http to allow for cross origin requests
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def homepage():
    """
    For GET/POST forms.
    If it comes from GET => empty graph
    else POST => find topics and graphs from files
    """

    json_topics = { }
    df_topics = None
    len_df = 0

    if request.method == 'POST':
        source = request.form.get('source')
        
        nodes_df = pd.read_csv(source+"_nodes.csv", sep=",")
        edges_df = pd.read_csv(source+"_edges.csv", sep=",")
        df_topics, json_topics = prepareGraph(nodes_df, edges_df)
        len_df = 1

    return render_template("index.html", topics=df_topics, 
            list_graph=json_topics, dispo=len_df)

if __name__=="__main__":
    app.run(debug=True, port=8000)
