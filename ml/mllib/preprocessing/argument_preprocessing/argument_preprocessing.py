import sys

import numpy as np
import pandas as pd
import sklearn.preprocessing

import gensim

from mllib.preprocessing.dataset_preparation import utils

"""
    Preprocessing of arguments:

     - apply models trained on document corpus to argument nodes
     - join arguments to their nodes
     - compute features specific to arguments (pairs of nodes)
"""


# Alter this function if you have some preprocessing you want to do 
# on individual nodes dictionary (prefer the DataFrame). 
# Look at first commented code block in preprocessed_argument_df()
#
# Please move it further down in the file (right after preprocessed_argument_df) when you do.
def preprocess_node(node): 
    # dict does not deep-copy objects: modify existing keys at your own risk
    #return dict(node, {
    #    #'new_feature1': 1, 'new_feature2': 2
    #})

    return node

def preprocessed_argument_df(
        argument_generator_getter,
        preprocessed_nodes_generator_getter,
        dictionary, tfidf_model,
        verbose = False,
    ):
    """
        Computes node features based on trained models (tf-idf).
        Joins arguments (on 'n1', 'n2') with nodes (on 'id').
        Computes argument features (tf-idf cosine similarity).

        Returns a DataFrame with all node features prefixed with
        premise_/conclusion_, and label in 'pro'.
    """
    if verbose:
        print("\n   ### preprocessed_argument_df() ###\n")

    # Single node preprocessing on generator items, as
    # a generator getter (untested)
    #preprocessed_nodes_generator_getter = lambda: map(
    #        preprocess_node,
    #        preprocessed_nodes_generator_getter())

    preprocessed_nodes = preprocessed_nodes_generator_getter()
    

    df_nodes = pd.DataFrame(preprocessed_nodes).set_index('id', drop=False)

    if verbose:
        print("node columns")
        print(df_nodes.info())
        print(df_nodes.describe())
        print("{} unique ids".format(len(df_nodes['id'].unique())))
        print("{} unique (id, debate_name)".format(
                len(pd.unique(
                    df_nodes[['id', 'debate_name']].values.ravel('K')
                ))
            ))
        print()

    # Drop node duplicates. They exist due to nodes appearing 
    # in multiple debates. 
    df_nodes.drop_duplicates(['id'], inplace=True)

    df_nodes['sparse_tfidf'] = df_nodes['lemmas'].apply(
            lambda lemmas: tfidf_model[dictionary.doc2bow(lemmas)])
                #[
                #    lemma for lemma in lemmas if lemma.isalpha() 
                #])])

    ### END OF NODE FEATURES

    # Get the columns of individual nodes. They need to be renamed
    # as they appear twice in arguments.
    node_columns = df_nodes.columns.values


    arguments = argument_generator_getter()
    df_arguments = pd.DataFrame(utils.merge_dicts(arguments))


    # Fit transformer for the label ('class')
    label_encoder = fit_label_encoder(argument_generator_getter)

    # Rename and encode 'class' column to 'pro'
    df_arguments['pro'] = label_encoder.transform(df_arguments['class'].values)
    df_arguments.drop(['class'], axis = 'columns', inplace = True)

    if verbose:
        print("argument columns before joining with nodes:")
        print(df_arguments.info())
        print(df_arguments.describe())
        print()

    # Join arguments with their nodes, prefixes with premise_/conclusion_,
    # and drops n1&n2 columns (renamed to prefix_id)
    df_arguments = df_arguments.join(
            other = df_nodes,
            on = 'n1', how = 'left'
    ).rename({
            column_name: 'premise_' + column_name
            for column_name in node_columns
        }, axis = 'columns'
    )

    if verbose:
        print("argument columns after joining with premises:")
        print(df_arguments.info())
        print(df_arguments.describe())
        print()

    df_arguments = df_arguments.join(
            other = df_nodes,
            on = 'n2', how = 'left'
    ).rename({
            column_name: 'conclusion_' + column_name
            for column_name in node_columns
        }, axis = 'columns'
    ).drop(['n1', 'n2'], axis = 'columns')


    # ARGUMENT FEATURES

    df_arguments['tfidf_cosine_similarity'] = \
            df_arguments[
                ['premise_sparse_tfidf', 'conclusion_sparse_tfidf']
            ].apply(
                lambda x: gensim.matutils.cossim(*x.values), axis = 'columns')



    # Reorder the columns placing argument columns last
    argument_columns = ['pro']
    df_arguments = df_arguments[
        [
            column for column in df_arguments.columns
            if column not in argument_columns
        ] + argument_columns
    ]
    
    if verbose:
        print("\n\nDataFrame after preprocessing:\n")

        print(df_arguments.info())
        print()

        print("Scalar columns statistics:")
        print(df_arguments.describe())
        print()

    return df_arguments

def fit_label_encoder(argument_generator_getter):
    """
        Map -1.0 to 0 and 1.0 to 1.
    """

    label_encoder = sklearn.preprocessing.LabelEncoder()
    label_encoder.fit(np.array([-1.0, 1.0]))

    return label_encoder

def fit_id_encoder(argument_generator_getter):
    """
        Encodes nodes ids to [0, nb_unique_ids - 1].
    """
    id_encoder = sklearn.preprocessing.OrdinalEncoder()
    id_encoder.fit([
        [n] 
        for argument in argument_generator_getter() 
        for n in argument[0].values()])

    return id_encoder

if __name__ == '__main__':
    pass
