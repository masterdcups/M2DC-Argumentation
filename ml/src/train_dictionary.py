import argparse
from pathlib import Path
import pickle as pkl

from mllib.preprocessing.text_preprocessing import text_preprocessing as text
from mllib.preprocessing.dataset_preparation import utils
from mllib import cfg

def main(preprocessed_node_path, argument_path, cfg_path, dictionary_path):
    preprocessed_node_path = Path(args.preprocessed_node_path)
    argument_path = Path(args.argument_path)
    cfg_path = Path(cfg_path)
    dictionary_path = Path(args.dictionary_path)

    dictionary_parameters = cfg.load(cfg_path)['dictionary']

    argument_generator_getter = lambda: utils.load(argument_path)

    argument_nodes_ids = set((
            node_id 
            for argument in argument_generator_getter()
            for node_id in argument[0].values())) 

    # Use the set of ids to select only the relevant nodes
    # (and not train nlp models on all documents).
    preprocessed_node_generator_getter = lambda : filter(
            lambda node: node['id'] in argument_nodes_ids,
            utils.load( preprocessed_node_path))

    dictionary = text.fit_dictionary(
            preprocessed_node_generator_getter,
            vocabulary_size = dictionary_parameters['vocabulary_size'],
            verbose = True)

    pkl.dump(dictionary, dictionary_path.open('wb'))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Fit Dictionary to corpus defined by argument nodes.')

    argparser.add_argument(
            'preprocessed_node_path',
            help='path to preprocessed node pickle file',
        )
    argparser.add_argument(
            'argument_path',
            help='path to argument pickle file',
        )
    argparser.add_argument(
            'cfg_path',
            help='path to configuration yaml file',
        )
    argparser.add_argument(
            'dictionary_path',
            help='path to dump dictionary',
        )
    args = argparser.parse_args()

    main(args.preprocessed_node_path, args.argument_path,
            args.cfg_path, args.dictionary_path)

