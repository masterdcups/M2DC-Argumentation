# Visualization

This is a web-based tool for visualizing the argument graph (pro/cons arguments) for a given topic.

You can add/edit/delete nodes and edges from the graph if it is necessary.

## Install
In a python environement do:
```sh
    conda install --yes --file requirements.txt
```
or:
```sh
    pip install requirements.txt
```
## Run
Run the following command:
```sh
    python main.py
```
Then, browse http://localhost:8000
## How to use:
1. Choose the files to load, it is needed both: nodes_csv and edges_csv.
2. Click the *Draw* button. This will take some time if the file is long.
3. The *Select Topic* bar will be filled with the recognized topics from the uploaded files.
4. Choose one topic.
    * To add a node it is better to choose some high ID value > 1000000, to avoid conflicts with the existing ones


