import keras

def data2layers(X, y=None):
    if not isinstance(X, dict):
        input_layers = keras.layers.Input(
            shape = X.shape[1:])
    else:
        input_layers = {
            input_name: keras.layers.Input(
                    name = input_name, 
                    shape = X[input_name].shape[1:]
                )
            for input_name in X
        }

    if y is None:
        return input_layers
    else:
        if not isinstance(y, dict):
            output_layers = keras.layers.Reshape(
                target_shape = y.shape[1:])
        else:
            output_layers = {
                output_name: keras.layers.Reshape(
                        name = output_name, 
                        target_shape = y[output_name].shape[1:]
                    )
                for output_name in y
            }

        return input_layers, output_layers
