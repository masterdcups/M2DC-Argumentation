import argparse
from pathlib import Path
import importlib
import pickle as pkl

import keras

from mllib import cfg
from mllib.preprocessing.dataset_preparation import utils
from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib import keras_utils
#from mllib.models import training, simple_models

import default_adaptor

def main(
        model_module_path, 
        training_argument_path, validation_argument_path,
        dictionary_path, tfidf_path,
        model_output_path
    ):
    model_module_path = Path(model_module_path)
    training_argument_path = Path(training_argument_path)
    validation_argument_path= Path(validation_argument_path)
    dictionary_path = Path(dictionary_path)
    tfidf_path = Path(tfidf_path)
    model_path = Path(model_output_path)


    model_module = importlib.import_module(model_module_path.stem)

    # Get a function mapping from data to model
    if hasattr(model_module, 'Adaptor'):
        adaptor = model_module.Adaptor()
    else:
        tfidf = pkl.load(tfidf_path.open('rb'))
        adaptor = default_adaptor.Adaptor(tfidf)



    # Get a sample of data and generate I/O layers from it.
    sample_generator = map(adaptor, ml_gen.generator_DataFrames(
        [lambda: pkl.load(training_argument_path.open('rb'))],
        batch_size = 2))
    sample_data = next(sample_generator)
    input_layers, output_layers = keras_utils.data2layers(*sample_data)
    del sample_generator

    # Load model and training parameters
    configuration = {}
    if hasattr(model_module, 'Configuration'):
        # We pass the sample data to the configuration,
        # as size of layers may depend on input size.
        configuration = model_module.Configuration(
                sample_X=sample_data[0],
                sample_y=sample_data[1])
    del sample_data
    model_configuration = configuration.get('model', {})
    fit_configuration = configuration.get('fit', {})


    model = model_module.Model(
            input_layers, output_layers, 
            **configuration['model'])
    model.summary()


    training_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(training_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64)))

    validation_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(validation_argument_path.open('rb'))],
                    batch_size = 32))
        
    model.fit_generator(
            training_generator, 
            steps_per_epoch = fit_configuration.get('steps_per_epoch', 100), 
            epochs = fit_configuration.get('epochs', 10),
            validation_data = validation_generator,
            validation_steps = 50
        )

    model.save(model_output_path)


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
            'dictionary_path',
            help='path to dictionary file',
        )
    argparser.add_argument(
            'tfidf_path',
            help='path to tfidf file',
        )
    argparser.add_argument(
            'model_output_path',
            help='path to dump trained model pickle', # hdf5 for NNs ?
        )
    args = argparser.parse_args()

    main(
            args.model_module_path, 
            args.training_argument_path, args.validation_argument_path,
            args.dictionary_path, args.tfidf_path,
            args.model_output_path)

