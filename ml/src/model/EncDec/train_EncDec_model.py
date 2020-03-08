import argparse
from pathlib import Path
import importlib
import pickle as pkl
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import keras
import keras.backend as K

from mllib import cfg
from mllib.preprocessing.text_preprocessing import embedder
from mllib.preprocessing.dataset_preparation import utils
from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib import keras_utils
#from mllib.models import training, simple_models

import default_adaptor



def main(model_module_path, 
        training_argument_path, validation_argument_path,
        word_embedding_path, sentiment_embedding_path,
        model_output_path
    ):
    model_module_path = Path(model_module_path)
    training_argument_path = Path(training_argument_path)
    validation_argument_path= Path(validation_argument_path)
    word_embedding_path = Path(word_embedding_path)
    model_output_path = Path(model_output_path)

    word_embedding_npz = np.load(word_embedding_path, allow_pickle=True)
    word_embedding_dictionary = embedder.tokens2dict(word_embedding_npz['tokens'])
    word_embedding_matrix = word_embedding_npz['embeddings']
    #vocab_size, embedded_size = word_embedding_matrix.shape

    sentiment_embedding_npz = np.load(sentiment_embedding_path, allow_pickle=True)
    sentiment_embedding_dictionary = embedder.tokens2dict(sentiment_embedding_npz['tokens'])
    sentiment_embedding_matrix = sentiment_embedding_npz['embeddings']
    #vocab_size, embedded_size = word_embedding_matrix.shape


    model_module = importlib.import_module(model_module_path.stem)

    # Get a function mapping from data to model
    if hasattr(model_module, 'Adaptor'):
        training_adaptor = model_module.Adaptor(
                word_embedding_dictionary=word_embedding_dictionary,
                sentiment_embedding_dictionary=sentiment_embedding_dictionary,
                augmentation_rate=0.1)
        validation_adaptor = model_module.Adaptor(
                word_embedding_dictionary=word_embedding_dictionary,
                sentiment_embedding_dictionary=sentiment_embedding_dictionary)
    else:
        raise ValueError("No adaptor in Cocarascu.py !")


    # Get a sample of data and generate I/O layers from it.
    sample_generator = map(training_adaptor, ml_gen.generator_DataFrames(
        [lambda: pkl.load(training_argument_path.open('rb'))],
        batch_size = 2, shuffle=True))
    sample_data = next(sample_generator)
    print(sample_data[0])
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

    for stream, values in sample_data[0].items():
        print(stream, np.min(values), np.mean(values), np.max(values), sep='  ')
    del sample_data


    model = model_module.Model(
            input_layers, output_layers, 
            word_matrix = word_embedding_matrix,
            sentiment_matrix = sentiment_embedding_matrix,
            **model_configuration)
    model.summary()
    keras.utils.plot_model(model, 'model_graph.png', 
            show_shapes=True, expand_nested=True, dpi=256)

    training_generator = map(training_adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(training_argument_path.open('rb'))],
                    batch_size = fit_configuration.get('batch_size', 64),
                    shuffle=True))


    validation_generator = map(validation_adaptor, 
                ml_gen.generator_DataFrames(
                    [lambda: pkl.load(validation_argument_path.open('rb'))],
                    #batch_size = fit_configuration.get('batch_size', 64),
                    epochs = 1,
                    shuffle=True))
    validation_data = next(validation_generator)

    if input('LR test ? y/[n] ')=='y': 
        lr_step_size = 500
        lr_finder = LR_Finder_log(
                mode='triangular', 
                base_lr=1e-4, max_lr=1e-0,
                step_size=lr_step_size)
        model.fit_generator(
                training_generator, 
                steps_per_epoch = lr_step_size, 
                epochs = 1,
                callbacks=[lr_finder]
            )
        plot_history(lr_finder.history, 'lr', 'log')
        return

    datetime_now = "{date:%Y-%m-%d-%H:%M:%S}".format(date=datetime.now())
    log_dir = model_output_path.parent / 'logs' / (model.name + ":" + datetime_now)
    log_dir.mkdir(parents=True)

    tensorboard = keras.callbacks.TensorBoard(
            log_dir=log_dir, write_graph=True
        )

    training_history = model.fit_generator(
            training_generator, 
            steps_per_epoch = fit_configuration.get('steps_per_epoch', 100), 
            epochs = fit_configuration.get('epochs', 10),
            validation_data = validation_data,
            #validation_steps = 50,
            callbacks = [tensorboard] + fit_configuration.get(
                'callbacks', [])
        ).history
    plot_history(training_history)


    metrics = {}
    metrics['training'] = model.evaluate_generator(
            training_generator,
            steps = 200,
        )
    metrics['validation'] = model.evaluate(
            *validation_data,
            batch_size = fit_configuration.get('batch_size', 64)
        )


    print("\ttrain\tval")
    for i, metric_name in enumerate(model.metrics_names):
        print("{}:".format(metric_name))

        print("\t{:.3f}\t{:.3f}".format(
            metrics['training'][i], metrics['validation'][i]))

    model.save(model_output_path)

def plot_history(history, x_axis_key=None, xscale=None):
    fig = plt.figure()


    for metric_name, metric_values in (x for x in history.items() if x[0] != 'lr'):
        if x_axis_key is not None:
            plt.plot(history[x_axis_key], metric_values, label=metric_name)
        else:
            plt.plot(metric_values, label=metric_name)
    axes = plt.gca()
    if xscale is not None:
        axes.set_xscale(xscale)
    axes.set_ylim([0,1])
    plt.legend()
    plt.show()

class LR_Finder_log(keras.callbacks.Callback):
    def __init__(self, base_lr=1e-5, max_lr=1e-0, step_size=2000., mode='triangular',
                 gamma=1., scale_fn=None, scale_mode='cycle'):
        super(LR_Finder_log, self).__init__()

        self.base_lr = base_lr
        self.max_lr = max_lr
        self.step_size = step_size
        self.mode = mode
        self.gamma = gamma
        if scale_fn == None:
            if self.mode == 'triangular':
                self.scale_fn = lambda x: 1.
                self.scale_mode = 'cycle'
            elif self.mode == 'triangular2':
                self.scale_fn = lambda x: 1/(2.**(x-1))
                self.scale_mode = 'cycle'
            elif self.mode == 'exp_range':
                self.scale_fn = lambda x: gamma**(x)
                self.scale_mode = 'iterations'
        else:
            self.scale_fn = scale_fn
            self.scale_mode = scale_mode
        self.clr_iterations = 0.
        self.trn_iterations = 0.
        self.history = {}

        self._reset()

    def _reset(self, new_base_lr=None, new_max_lr=None,
               new_step_size=None):
        """Resets cycle iterations.
        Optional boundary/step size adjustment.
        """
        if new_base_lr != None:
            self.base_lr = new_base_lr
        if new_max_lr != None:
            self.max_lr = new_max_lr
        if new_step_size != None:
            self.step_size = new_step_size
        self.clr_iterations = 0.
        
    def clr(self):
        cycle = np.floor(1+self.clr_iterations/(2*self.step_size))
        x = np.abs(self.clr_iterations/self.step_size - 2*cycle + 1)

        base_lr_log = np.log(self.base_lr)
        lr_range_log = np.log(self.max_lr) - base_lr_log
        return np.exp(base_lr_log + lr_range_log * np.maximum(0, (1-x)))
        
    def on_train_begin(self, logs={}):
        logs = logs or {}

        if self.clr_iterations == 0:
            K.set_value(self.model.optimizer.lr, self.base_lr)
        else:
            K.set_value(self.model.optimizer.lr, self.clr())        
            
    def on_batch_end(self, epoch, logs=None):
        
        logs = logs or {}
        self.trn_iterations += 1
        self.clr_iterations += 1

        self.history.setdefault('lr', []).append(K.get_value(self.model.optimizer.lr))
        self.history.setdefault('iterations', []).append(self.trn_iterations)

        for k, v in logs.items():
            self.history.setdefault(k, []).append(v)
        
        K.set_value(self.model.optimizer.lr, self.clr())


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
            'word_embedding_path',
            help='path to embedding .npz file',
        )
    argparser.add_argument(
            'sentiment_embedding_path',
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
            args.word_embedding_path, args.sentiment_embedding_path,
            args.model_output_path)

