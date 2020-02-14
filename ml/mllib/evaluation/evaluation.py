import sys
import pickle as pkl

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix

from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad


def evaluate_simple(
        model, 
        training_df_loaders, validation_df_loaders,
        parameters):

    generator = lambda df_loaders: map(
            lambda batch: (batch['X'], batch['y']),
            ml_gen.generator_DataFrame2numpy(
                df_loaders,
                ml_ad.default_DataFrame2numpy_mapping(parameters),
                batch_size = None, epochs = 1,
                default_transform = ml_ad.default_DataFrame2numpy_transform,
            )
        )


    print("Training metrics:")
    X, y = next(generator(training_df_loaders))
    y_prediction = model.predict(X) > 0.5

    print("Confusion matrix:")
    print(confusion_matrix(y, y_prediction))
    print("Accuracy:", accuracy_score(y, y_prediction))
    print()


    print("Validation metrics:")
    X, y = next(generator(validation_df_loaders))
    y_prediction = model.predict(X) > 0.5

    print("Confusion matrix:")
    print(confusion_matrix(y, y_prediction))
    print("Accuracy:", accuracy_score(y, y_prediction))



if __name__ == '__main__':
    model = pkl.load(open(sys.argv[1], 'rb'))
    evaluation_df_loaders = [lambda: pkl.load(open(sys.argv[2], 'rb'))]

    evaluate_simple(model, evaluation_df_loaders)
