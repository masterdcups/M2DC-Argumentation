import numpy as np
import keras
import keras.backend as K

from keras.layers import (
        Input, Embedding,
        Reshape, RepeatVector, Concatenate, Flatten,
        Add, Multiply, Dot,
        Lambda,
        Dense, RNN, GRU, LSTM, Conv1D,
        LeakyReLU, Softmax,
        Bidirectional,
        Dropout, BatchNormalization,
    )
from keras.optimizers import Adam

def Model(input_layer, output_layer, 
        projection_dimension = 16,
        projection_activation = 'relu',
        projection_dropout = 0.5,
        loss = 'binary_crossentropy',
        optimizer = Adam(),
        metrics = ['binary_accuracy'],
        name = 'MLP'
    ):

    x = input_layer
    
    projection = Dense(projection_dimension, 
            activation = projection_activation
        )(x)
    projection = Dropout(projection_dropout)(projection)

    prediction = Dense(1, activation='sigmoid')(projection)

    pro = output_layer(prediction)

    model = keras.models.Model(
            inputs=[x], outputs=[pro], 
            name = name)

    model.compile(
            loss = loss,
            metrics = metrics,
            optimizer = optimizer
        )

    return model

def Configuration(
        sample_X = np.ones((2, 1000)), 
        **kwargs
    ):
    configuration = {
        'model': {
            'projection_dimension': int(np.sqrt(sample_X.shape[-1])),
            'projection_dropout': 0.25
        },
        'fit': {
            'batch_size': 64
        }
    }
    return configuration





if __name__ == '__main__':
    import numpy as np

    in_shape = (2000,)
    out_shape = (1,)

    input_layer = keras.layers.Input(shape=in_shape)
    output_layer = keras.layers.Reshape(target_shape=out_shape)

    parameters = {'projection_activation': 'linear'}
    config = Configuration()['model']
    model = Model(
            input_layer, output_layer, 
            **config)

    print()
    model.summary()
    print()

    model.fit(
            np.ones((5000, in_shape[0])), 
            np.zeros((5000, out_shape[0])), 
            batch_size = config['training']['batch_size'], 
            epochs = config['training']['epochs'])

