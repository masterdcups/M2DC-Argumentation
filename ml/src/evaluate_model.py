import argparse
from pathlib import Path

import pickle as pkl

import sklearn

from mllib import cfg

from mllib.preprocessing.dataset_preparation import utils
from mllib.evaluation import evaluation


def main(model_path, training_argument_path, validation_argument_path,
        dictionary_cfg_path):
        #evaluation_path):

    model_path = Path(model_path)
    training_argument_path = Path(training_argument_path)
    validation_argument_path= Path(validation_argument_path)
    dictionary_cfg_path = Path(dictionary_cfg_path)

    model = pkl.load(model_path.open('rb'))
    model = evaluation.evaluate_simple(model,
            [lambda: pkl.load(training_argument_path.open('rb'))], 
            [lambda: pkl.load(validation_argument_path.open('rb'))], 
            cfg.load_merge([dictionary_cfg_path]))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Creates pandas.DataFrame pickle file for preprocessed arguments'
        )
    argparser.add_argument(
            'training_argument_path',
            help='path to training argument file',
        )
    argparser.add_argument(
            'validation_argument_path',
            help='path to validation argument file',
        )
    argparser.add_argument(
            'dictionary_cfg_path',
            help='path to dictionary cfg file',
        )
    argparser.add_argument(
            'model_path',
            help='path to dump trained model pickle', # hdf5 for NNs ?
        )
    args = argparser.parse_args()

    main(args.training_argument_path, args.validation_argument_path,
            args.dictionary_cfg_path,
            args.model_path)

