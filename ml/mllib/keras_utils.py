import keras

def data2layers(X, y=None):
    def data2shape(data):
        nb_dimensions = data.ndim
        shape = data.shape
        trimmed_shape = \
            shape if shape[-1] != 1 else shape[:-1]

        nb_dimensions = len(trimmed_shape)

        proposed_shape = (
                (None, shape[-1])
                if len(shape) == 3 else
                shape[-1:]
            )
        print(shape, proposed_shape)
        return proposed_shape

        if nb_dimensions == 2:
            return (None, shape[-1])
        else:
            return shape[1:]

    if not isinstance(X, dict):
        input_layers = keras.layers.Input(
            shape = data2shape(X))
    else:
        for input_name in X:
            #print("layer {}".format(input_name))
            data = X[input_name]
            shape = data.shape
            #print("shape: {}".format(shape))
            trimmed_shape = \
                shape if shape[-1] != 1 else shape[:-1]
            #print("trimmed: {}".format(trimmed_shape))
            proposed_shape = (
                    (None, shape[-1])
                    if len(shape) == 3 else
                    shape
                )
            #print("proposed: {}".format(proposed_shape))
            #print()


        input_layers = {
            input_name: keras.layers.Input(
                    name = input_name, 
                    shape = data2shape(X[input_name])
                )
            for input_name in X
        }

    if y is None:
        return input_layers
    else:
        if not isinstance(y, dict):
            output_layers = keras.layers.Reshape(
                target_shape = data2shape(y))
        else:
            output_layers = {
                output_name: keras.layers.Reshape(
                        name = output_name, 
                        target_shape = data2shape(y[output_name])
                    )
                for output_name in y
            }

        return input_layers, output_layers
