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

def Model(input_layer, output_layer, parameters={}):
    # More generally, with an input_layers dict:
    #input_feature1 = input_layers['feature1']
    #input_bad_feature = input_layers['best_feature']
    x = input_layer
    
    projection = Dense(
            parameters.get('projection_dimensions', 16), 
            activation=parameters.get('projection_activation', 'relu')
        )(x)

    prediction = Dense(1, activation='sigmoid')(projection)

    #pro = output_layers['pro'](prediction)
    pro = output_layer(prediction)

    model = keras.models.Model(
            inputs=[x], outputs=[pro], 
            name=parameters.get('name', 'ReLU-16'))

    model.compile(
            loss = parameters.get('loss', 'binary_crossentropy'),
            metrics = parameters.get('metrics', ['binary_accuracy']),
            optimizer = parameters.get('optimizer', Adam()))

    return model

if __name__ == '__main__':
    import numpy as np

    in_shape = (2000,)
    out_shape = (1,)

    input_layer = keras.layers.Input(shape=in_shape)
    output_layer = keras.layers.Reshape(target_shape=out_shape)

    model = Model(
            input_layer, output_layer, 
            parameters={'projection_activation': 'linear'})

    print()
    model.summary()
    print()

    model.fit(
            np.ones((5000, in_shape[0])), 
            np.zeros((5000, out_shape[0])), 
            batch_size = 64, epochs=5)

