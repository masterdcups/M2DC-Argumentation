"""
Main

For now it is more like a sample run:
 - Create and dump a generator of raw sentences (text+n) if missing
 - Create and dump a generator of raw arguments (n1+n2+w) if missing
 - Load the raw data generators
 - Apply an arbitrary transformation (to upper case)
 - Map the argument generator with sentence texts
 - Print a few lines

"""

import utils
import datasets
import py2neo
import os
import argparse



def main(dataset_name, n4j_uri, n4j_auth):
    """Sample run"""

    raw_sentences_dump_file = os.path.join('datasets', 'sentences.pkl')
    raw_arguments_dump_file = os.path.join('datasets', dataset_name+'.pkl')


    # Create raw datasets (if missing) 
    n4j_graph = None
   
    if not os.path.isfile(raw_sentences_dump_file):
        print("Create raw-sentence-dataset")
        if n4j_graph is None:
            n4j_graph = py2neo.Graph(n4j_uri, auth=n4j_auth)
        gen = datasets.sentence_generator(n4j_graph)
        utils.dump(gen, raw_sentences_dump_file)

    if not os.path.isfile(raw_arguments_dump_file):
        print("Create raw-arguments-dataset")
        if n4j_graph is None:
            n4j_graph = py2neo.Graph(n4j_uri, auth=n4j_auth)
        gen = datasets.argument_generator(dataset_name, n4j_graph)
        utils.dump(gen, raw_arguments_dump_file)


    # Load dumped datasets
    sgen = utils.load(raw_sentences_dump_file)
    agen = utils.load(raw_arguments_dump_file)

    # Apply an arbitrary transformation on sentences (to upper)
    sgen = utils.gmap(sgen, lambda rec: {'s': rec['s'].upper(), 'n': rec['n']})

    # Map the sentences over the arguments
    agen = utils.gmap(agen, datasets.sentence_mapper(sgen))

    # Print rows
    for X, y in agen:
        print(X['s1'][:30], X['s2'][:30], y['class'], sep="\t")


if __name__ == "__main__":

    # Read command-line arguments
    parser = argparse.ArgumentParser(description="Sample run")
    parser.add_argument('dataset_name', nargs='?', default='dev2')
    parser.add_argument('--n4j_uri', nargs='?', default='bolt://localhost:7687')
    parser.add_argument('--n4j_user', nargs='?', default='neo4j')
    parser.add_argument('--n4j_pass', nargs='?', default="")
    args = parser.parse_args()

    # Let's-a-go !
    main(args.dataset_name, args.n4j_uri, (args.n4j_user,args.n4j_pass))

        
