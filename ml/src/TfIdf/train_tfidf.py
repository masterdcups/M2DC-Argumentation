import argparse
from pathlib import Path
import pickle as pkl

from mllib.preprocessing.text_preprocessing import text_preprocessing as text
from mllib.preprocessing.dataset_preparation import utils

from TfIdf import TfIdf

def main(preprocessed_node_path, argument_path, dictionary_path, tfidf_path):
    preprocessed_node_path = Path(args.preprocessed_node_path)
    argument_path = Path(args.argument_path)
    dictionary_path = Path(args.dictionary_path)
    tfidf_path = Path(args.tfidf_path)

    #argument_generator_getter = lambda: utils.load(argument_path)

    #argument_nodes_ids = set((
    #        node_id 
    #        for argument in argument_generator_getter()
    #        for node_id in argument[0].values())) 

    # Use the set of ids to select only the relevant nodes
    # (and not train nlp models on all documents).
    #preprocessed_node_generator_getter = lambda : filter(
    #        lambda node: node['id'] in argument_nodes_ids,
    #        utils.load( preprocessed_node_path))

    dictionary = pkl.load(dictionary_path.open('rb'))

    #tfidf = text.fit_tfidf(preprocessed_node_generator_getter,
    #        dictionary,
    #        verbose = True)
    tfidf = TfIdf()
    tfidf.fit(dictionary.dictionary)
    tfidf.save(tfidf_path)

    #pkl.dump(tfidf, tfidf_path.open('wb'))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Fit Tf-Idf model to corpus defined by argument nodes.')

    argparser.add_argument(
            'preprocessed_node_path',
            help='path to preprocessed node pickle file',
        )
    argparser.add_argument(
            'argument_path',
            help='path to argument pickle file',
        )
    argparser.add_argument(
            'dictionary_path',
            help='path to dictionary pickle file',
        )
    argparser.add_argument(
            'tfidf_path',
            help='path to dump tfidf model',
        )
    args = argparser.parse_args()

    main(args.preprocessed_node_path, args.argument_path, 
            args.dictionary_path,
            args.tfidf_path)

