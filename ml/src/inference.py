import argparse
from pathlib import Path
import importlib
import pickle as pkl
from datetime import datetime
import operator

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras
import keras.backend as K

from TextPreprocessor import TextPreprocessor


from mllib import cfg
from mllib.preprocessing.text_preprocessing import embedder
from mllib.preprocessing.dataset_preparation import utils
from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib import keras_utils

def main(
        model_module_path, model_path, 
        word_embedding_path,
        sentiment_embedding_path
    ):

    model_module_path = Path(model_module_path)
    model_path = Path(model_path)

    model = keras.models.load_model(model_path)



    # Load embedding dictionaries
    word_embedding_npz = np.load(word_embedding_path, allow_pickle=True)
    word_embedding_dictionary = embedder.tokens2dict(word_embedding_npz['tokens'])
    sentiment_embedding_npz = np.load(sentiment_embedding_path, allow_pickle=True)
    sentiment_embedding_dictionary = embedder.tokens2dict(sentiment_embedding_npz['tokens'])

    model_module = importlib.import_module(model_module_path.stem)
    # Get a function mapping from data to model
    if hasattr(model_module, 'Adaptor'):
        adaptor = model_module.Adaptor(
                word_embedding_dictionary=word_embedding_dictionary,
                sentiment_embedding_dictionary=sentiment_embedding_dictionary,
                inference=True)
    else:
        raise ValueError("No adaptor found !")

    # Load and prepare arguments.
    arguments = [
        (
            'Banana is the best fruit.',
            'They are full of potassium, which helps with cramps and is good for your health.'
        ),
        (
            'Banana is the best fruit.',
            'Bananas are yellow. Yellow is bad, I hate it. Therefore bananas are horrible.'
        ),
    ]
    premises = map(operator.itemgetter(1), arguments)
    conclusions = map(operator.itemgetter(0), arguments)

    txt_preprocessor = TextPreprocessor()

    premises = txt_preprocessor.transform(premises)
    conclusions = txt_preprocessor.transform(conclusions)

    df_premises = pd.DataFrame(premises)
    df_premises = df_premises.rename({
            column_name: 'premise_' + column_name
            for column_name in df_premises.columns
        }, axis = 'columns'
    )
    df_conclusions = pd.DataFrame(conclusions)
    df_conclusions = df_conclusions.rename({
            column_name: 'conclusion_' + column_name
            for column_name in df_conclusions.columns
        }, axis = 'columns'
    )

    df_arguments = pd.concat([df_premises, df_conclusions], axis='columns')
    
    argument_generator = map(adaptor, ml_gen.generator_DataFrames(
        [lambda: df_arguments], batch_size=None))

    predictions = model.predict_generator(
            argument_generator,
            steps=1)

    print(predictions)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Trains and save a keras model'
        )
    argparser.add_argument(
            'model_module_path',
            help='path to model.py file',
        )

    argparser.add_argument(
            'model_path',
            help='path of trained model',
        )
    argparser.add_argument(
            'word_embedding_path',
            help='path to embedding .npz file',
        )
    argparser.add_argument(
            'sentiment_embedding_path',
            help='path to embedding .npz file',
        )

    args = argparser.parse_args()

    main( args.model_module_path, args.model_path,
            args.word_embedding_path, args.sentiment_embedding_path)

