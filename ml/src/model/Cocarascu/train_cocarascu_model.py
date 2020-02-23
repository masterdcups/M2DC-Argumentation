import argparse
from pathlib import Path
import importlib
import pickle as pkl

import numpy as np
import keras

from mllib import cfg
from mllib.preprocessing.text_preprocessing import embedder
from mllib.preprocessing.dataset_preparation import utils
from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib import keras_utils
#from mllib.models import training, simple_models

import default_adaptor



def main(model_module_path, 
        training_argument_path, validation_argument_path,
        embedding_path,
        model_output_path
    ):
    model_module_path = Path(model_module_path)
    training_argument_path = Path(training_argument_path)
    validation_argument_path= Path(validation_argument_path)
    embedding_path = Path(embedding_path)
    model_output_path = Path(model_output_path)

    embedding_npz = np.load(embedding_path, allow_pickle=True)
    token2id_dictionary = embedder.tokens2dict(embedding_npz['tokens'])
    embedding_matrix = embedding_npz['embeddings']
    vocab_size, embedded_size = embedding_matrix.shape
    print("###")
    print(vocab_size, embedded_size)
    print("###")

    model_module = importlib.import_module(model_module_path.stem)

    # Get a function mapping from data to model
    if hasattr(model_module, 'Adaptor'):
        adaptor = model_module.Adaptor(token2id=token2id_dictionary)
    else:
        raise ValueError("No adaptor in Cocarascu.py !")


    # Get a sample of data and generate I/O layers from it.
    sample_generator = map(adaptor, ml_gen.generator_DataFrames(
        [lambda: pkl.load(training_argument_path.open('rb'))],
        batch_size = 2))
    sample_data = next(sample_generator)
    input_layers, output_layers = keras_utils.data2layers(*sample_data)
    del sample_generator

    # Load model and training parameters
    model_configuration = {}
    fit_configuration = {}
    if hasattr(model_module, 'ModelCfg'):
        # We pass the sample data to the configuration,
        # as size of layers may depend on input size.
        model_configuration = model_module.ModelCfg(
                sample_X=sample_data[0],
                sample_y=sample_data[1])
    if hasattr(model_module, 'FitCfg'):
        # We pass the sample data to the configuration,
        # as size of layers may depend on input size.
        fit_configuration = model_module.FitCfg(
                sample_X=sample_data[0],
                sample_y=sample_data[1])
    del sample_data


    model = model_module.Model(
            input_layers, output_layers, 
            embedding_matrix = embedding_matrix,
            vocab_size = vocab_size, embedded_size = embedded_size,
            **model_configuration)
    model.summary()


    training_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(training_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64)))

    validation_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(validation_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64)))
        
    model.fit_generator(
            training_generator, 
            steps_per_epoch = fit_configuration.get('steps_per_epoch', 100), 
            epochs = fit_configuration.get('epochs', 10),
            validation_data = validation_generator,
            validation_steps = 50
        )

    model.save(model_output_path)

    metrics = {}
    metrics['training'] = model.evaluate_generator(
            training_generator,
            steps = 200,
        )
    metrics['validation'] = model.evaluate_generator(
            validation_generator,
            steps = 50,
        )


    print("\ttrain\tval")
    for i, metric_name in enumerate(model.metrics_names):
        print("{}:".format(metric_name))

        print("\t{:.3f}\t{:.3f}".format(
            metrics['training'][i], metrics['validation'][i]))




if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Trains and save a keras model'
        )
    argparser.add_argument(
            'model_module_path',
            help='path to model.py file',
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
            'embedding_path',
            help='path to embedding .npz file',
        )
    argparser.add_argument(
            'model_output_path',
            help='path to dump trained model pickle', # hdf5 for NNs ?
        )
    args = argparser.parse_args()

    main(
            args.model_module_path, 
            args.training_argument_path, args.validation_argument_path,
            args.embedding_path,
            args.model_output_path)

