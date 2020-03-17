import argparse
from pathlib import Path
import pickle as pkl

from mllib import cfg

from mllib.preprocessing.dataset_preparation import utils
from mllib.preprocessing.argument_preprocessing import \
        argument_preprocessing as arg_prep

def main(argument_path, preprocessed_node_path,
        dictionary_path, tfidf_path, 
        preprocessed_argument_path):

    argument_path = Path(argument_path)
    preprocessed_node_path= Path(preprocessed_node_path)
    dictionary_path = Path(dictionary_path)
    tfidf_path = Path(tfidf_path)
    preprocessed_argument_path = Path(preprocessed_argument_path)

    dictionary = pkl.load(dictionary_path.open('rb'))
    tfidf = pkl.load(tfidf_path.open('rb'))


    preprocessed_argument_df = arg_prep.preprocessed_argument_df(
            lambda: utils.load(argument_path),
            lambda: utils.load(preprocessed_node_path),
            dictionary, tfidf, verbose=True)


    pkl.dump(preprocessed_argument_df, preprocessed_argument_path.open('wb'))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Creates pandas.DataFrame pickle file for preprocessed arguments'
        )
    argparser.add_argument(
            'argument_path',
            help='path to argument pickle file',
        )
    argparser.add_argument(
            'preprocessed_node_path',
            help='path to preprocessed node pickle file',
        )
    argparser.add_argument(
            'dictionary_path',
            help='path to dictionary pickle file',
        )
    argparser.add_argument(
            'tfidf_path',
            help='path to the tfidf model pickle file',
        )
    argparser.add_argument(
            'preprocessed_argument_path',
            help='path to dump preprocessed argument pickle (DataFrame)',
        )
    args = argparser.parse_args()

    main(args.argument_path, args.preprocessed_node_path,
            args.dictionary_path, args.tfidf_path,
            args.preprocessed_argument_path)

