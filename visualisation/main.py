import json
import pandas as pd
from flask import Flask, request, render_template
from utils import *

# Serve the file over http to allow for cross origin requests
app = Flask(__name__)


@app.route('/jsonFile', methods=['GET', 'POST'])
def ajaxFunc():
    """
    Service for retrieving JSON file with the graph format
    to display it in the web using JS
    """

    source = request.args.get('source')
    topic = request.args.get('topic')   
    #print(source,topic)

    if source is None or topic is None:
        bJson = json.dumps({"nodes":[], "edges":[]})
        return bJson

    path = "json/"+str(source)+"/"+str(topic)
    bJson = None
    with open(path) as jsonFile:
        bJson = json.load(jsonFile)
    return bJson


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
        #nodes_df = pd.read_csv(source+"_nodes.csv", sep=",")
        #edges_df = pd.read_csv(source+"_edges.csv", sep=",")
        #df_topics, json_topics = prepareGraph(nodes_df, edges_df)
        df_topics = pd.read_csv("json/"+source+"/listTopics.csv", sep="\t", names=['id','name'])
        len_df = 1

    #print(df_topics)
    return render_template("index.html", topics=df_topics, 
            list_graph=json_topics, dispo=len_df)


if __name__=="__main__":
    app.run(debug=True, port=8000)
