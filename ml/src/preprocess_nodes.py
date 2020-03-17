import argparse
from pathlib import Path
import pickle as pkl

from tqdm import tqdm

from mllib.preprocessing.text_preprocessing import text_preprocessing as text
from mllib.preprocessing.dataset_preparation import utils

from TextPreprocessor import TextPreprocessor

def main(node_path, arguments_path, preprocessed_node_path):
    """
        Load nodes and edges lists, select nodes appearing in the edge list
        and apply NLP transformations (lemmatization, pos tagging).
    """

    node_path = Path(node_path)
    preprocessed_node_path = Path(preprocessed_node_path)
    arguments_path = Path(arguments_path)

    arguments_getter = lambda: utils.load(arguments_path)
    node_ids = set((
            node_id 
            for argument in arguments_getter()
            for node_id in argument[0].values())) 


    node_generator_getter = lambda: utils.load(node_path)
    filtered_nodes_getter = lambda: filter(
            lambda node: node['n'] in node_ids,
            node_generator_getter())


    text_preprocessor = TextPreprocessor()
    preprocessed_text_generator = text_preprocessor.transform(
            map(lambda node: node['s'], filtered_nodes_getter()))


    renamed_node_generator = map(
            lambda node: {
                    'id': node['n'],
                    'document': node['s'],
                    'debate_name': node['debate_name']
                },
            filtered_nodes_getter())

    preprocessed_node_generator = utils.merge_dicts(zip(
        renamed_node_generator, preprocessed_text_generator))

    utils.dump(tqdm(preprocessed_node_generator), preprocessed_node_path)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Corpus agnostic transformation for node documents.')

    argparser.add_argument(
            'node_path',
            help='path to node pickle file (sentences.pkl)',
        )
    argparser.add_argument(
            'arguments_path',
            help='path to arguments pickle file (used to filter node ids)',
        )
    argparser.add_argument(
            'preprocessed_node_path',
            help='path of the preprocessed file to create' +
                '(might be suffixed with _xx)',
        )
    args = argparser.parse_args()

    main(args.node_path, args.arguments_path,
        args.preprocessed_node_path)

