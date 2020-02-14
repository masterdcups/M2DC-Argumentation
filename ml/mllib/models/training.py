import sys
from pathlib import Path
import pickle as pkl

import numpy as np
import pandas as pd

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from mllib.preprocessing.ml_preprocessing import ml_generators as ml_gen
from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad

def fit_simple(model,
        training_df_loaders,
        validation_df_loaders,
        parameters = None,
    ):

    # Whole training file, with default mapping
    training_generator = map(
            lambda batch: (batch['X'], batch['y']),
            ml_gen.generator_DataFrame2numpy(
                training_df_loaders,
                ml_ad.default_DataFrame2numpy_mapping(parameters),
                batch_size = None, epochs = 1,
                default_transform = ml_ad.default_DataFrame2numpy_transform,
            ))

    X_train, y_train = next(training_generator)
    del training_generator

    model.fit(X_train, y_train)

    return model


# Using pathlib to get all files matching suffix.*prefix in a directory.
#preprocessed_arguments_dir_path = Path(preprocessed_arguments_dir)
#
#regex_pattern = '{}.*{}'.format(prefix, suffix)
#preprocessed_arguments_files_paths = [
#    path
#    for path in preprocessed_arguments_dir_path.iterdir()
#    if not path.isdir() and re.match(regex_pattern, f.name)
#]

if __name__ == '__main__':
    training_df_loaders = [lambda: pkl.load(open(sys.argv[1], 'rb'))]
    validation_df_loaders = [lambda: pkl.load(open(sys.argv[2], 'rb'))]
    output_dir = sys.argv[3]

    model = LogisticRegression()
    model = fit_simple(model, training_df_loaders, validation_df_loaders)

    pkl.dump(model, (Path(output_dir) / 'model.pkl').open('wb'))
    print("Done.")
