import argparse
from pathlib import Path
import pickle as pkl

from mllib.preprocessing.text_preprocessing import text_preprocessing as text
from mllib.preprocessing.dataset_preparation import utils

def main(node_path, preprocessed_node_path):
    node_path = Path(node_path)
    preprocessed_node_path = Path(preprocessed_node_path)

    preprocessed_node_generator = text.preprocessed_node_generator(
            lambda: utils.load(node_path))

    utils.dump(preprocessed_node_generator, preprocessed_node_path)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Corpus agnostic transformation for node documents.')

    argparser.add_argument(
            'node_path',
            help='path to node pickle file (sentences.pkl)',
        )
    argparser.add_argument(
            'preprocessed_node_path',
            help='path of the preprocessed file to create' +
                '(might be suffixed with _xx)',
        )
    args = argparser.parse_args()

    main(args.node_path, args.preprocessed_node_path)

