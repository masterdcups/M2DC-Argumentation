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
        model_save_path,
        training_argument_path, validation_argument_path,
        dictionary_path, tfidf_path,
        evaluation_output_path
    ):
    model_module_path = Path(model_module_path)
    model_save_path = Path(model_save_path)
    training_argument_path = Path(training_argument_path)
    validation_argument_path= Path(validation_argument_path)
    dictionary_path = Path(dictionary_path)
    tfidf_path = Path(tfidf_path)
    evaluation_output_path = Path(evaluation_output_path)


    model_module = importlib.import_module(model_module_path.stem)

    if hasattr(model_module, 'Adaptor'):
        adaptor = model_module.Adaptor()
    else:
        tfidf = pkl.load(tfidf_path.open('rb'))
        adaptor = default_adaptor.Adaptor(tfidf)

    # Select only X
    #adaptor = lambda x: adaptor(x)[0]

    # Get a sample of data and generate I/O layers from it.
    sample_generator = map(adaptor, ml_gen.generator_DataFrames(
        [lambda: pkl.load(training_argument_path.open('rb'))],
        batch_size = 2))
    sample_data = next(sample_generator)
    del sample_generator


    # Load model and training parameters
    configuration = {}
    if hasattr(model_module, 'Configuration'):
        # We pass the sample data to the configuration,
        # as size of layers may depend on input size.
        configuration = model_module.Configuration(
                sample_X=sample_data[0],
                sample_y=sample_data[1])

    model_configuration = configuration.get('model', {})
    fit_configuration = configuration.get('fit', {})

    del sample_data

    model = keras.models.load_model(model_save_path)

    model.summary()


    training_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(training_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64)))

    validation_generator = map(adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(validation_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64)))
        
    metrics = {}
    metrics['training'] = model.evaluate_generator(
            training_generator, 
            steps = 200,
        )
    metrics['validation'] = model.evaluate_generator(
            validation_generator, 
            steps = 50,
        )


    with evaluation_output_path.open('w') as f:
        print("\ttrain\tval")
        f.write("\ttrain\tval")
        for i, metric_name in enumerate(model.metrics_names):
            f.write("{}:".format(metric_name))
            f.write("\t{:.3f}\t{:.3f}".format(metrics['training'][i], metrics['validation'][i]))
            print("{}:".format(metric_name))
            print("\t{:.3f}\t{:.3f}".format(metrics['training'][i], metrics['validation'][i]))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description='Evaluates a keras model'
        )
    argparser.add_argument(
            'model_module_path',
            help='path to model.py',
        )
    argparser.add_argument(
            'model_save_path',
            help='path to model.h5',
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
            'evaluation_output_path',
            help='path to dump evaluation',
        )
    args = argparser.parse_args()

    main(
            args.model_module_path, args.model_save_path,
            args.training_argument_path, args.validation_argument_path,
            args.dictionary_path, args.tfidf_path,
            args.evaluation_output_path)

