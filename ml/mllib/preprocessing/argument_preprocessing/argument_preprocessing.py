import sys

import numpy as np
import pandas as pd
import sklearn.preprocessing as sk_preprocessing

import gensim

from mllib.preprocessing.dataset_preparation import utils

def fit_label_encoder(argument_generator_getter):
    """
        Map -1.0 to 0 and 1.0 to 1.
    """

    label_encoder = sk_preprocessing.LabelEncoder()
    label_encoder.fit(np.array([-1.0, 1.0]))

    return label_encoder

def fit_id_encoder(argument_generator_getter):
    """
        Encodes nodes ids to [0, nb_unique_ids - 1].
    """
    id_encoder = sk_preprocessing.OrdinalEncoder()
    id_encoder.fit([
        [n] 
        for argument in argument_generator_getter() 
        for n in argument[0].values()])

    return id_encoder


def preprocessed_argument_df(
        argument_generator_getter,
        nodes_nlp_generator_getter,
        dictionary, tfidf_model,
        verbose = False,
    ):
    """
        Computes node features based on trained models (tf-idf).
        Joins arguments (on 'n1', 'n2') with nodes (on 'id').
        Computes argument features (tf-idf cosine similarity).

        Returns a DataFrame with all node features prefixed with
        premise_/conclusion_, and class in 'pro'.
    """


    nodes_nlp = nodes_nlp_generator_getter()
    df_nodes = pd.DataFrame(nodes_nlp).set_index('id', drop=False)

    df_nodes['sparse_tfidf'] = df_nodes['lemmas'].apply(
            lambda lemmas: tfidf_model[
                dictionary.doc2bow([
                    lemma for lemma in lemmas if lemma.isalpha() ]) ] )

    node_columns = df_nodes.columns.values

    label_encoder = fit_label_encoder(argument_generator_getter)

    arguments = argument_generator_getter()
    df_arguments = pd.DataFrame(utils.merge_dicts(arguments))


    # Join arguments with their nodes, prefixes with premise_/conclusion_,
    # and drops n1&n2 columns (renamed to prefix_id)
    df_arguments = df_arguments.join(
            other = df_nodes,
            on = 'n1', how = 'inner'
    ).rename({
            column_name: 'premise_' + column_name
            for column_name in node_columns
        }, axis = 'columns'
    ).join(
            other = df_nodes,
            on = 'n2', how = 'inner'
    ).rename({
            column_name: 'conclusion_' + column_name
            for column_name in node_columns
        }, axis = 'columns'
    ).drop(['n1', 'n2'], axis = 'columns')

    df_arguments['tfidf_cosine_similarity'] = \
            df_arguments[
                ['premise_sparse_tfidf', 'conclusion_sparse_tfidf']
            ].apply(
                lambda x: gensim.matutils.cossim(*x.values), axis = 'columns')

    # Rename and encode 'class' column to 'pro'
    df_arguments['pro'] = label_encoder.transform(df_arguments['class'].values)
    df_arguments.drop(['class'], axis = 'columns', inplace = True)

    
    if verbose:
        print("\nDataFrame after preprocessing:")

        print(df_arguments.columns.values)
        print()

        print(df_arguments.info())
        print()

        print(df_arguments.describe())
        print()

    return df_arguments

if __name__ == '__main__':
    pass
