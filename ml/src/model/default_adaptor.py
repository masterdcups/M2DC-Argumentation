import numpy as np

from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad

def Adaptor(
        tfidf, embedder,
        merge_X=True, merge_y=True
    ):
    """ Maps a preprocessed arguments DataFrame columns to a dictionary
    of np.array keyed by ['X'|'y'], followed by ['name'] if the columns
    were not merged (merge_X and merge_y).
    """

    mean_embedding = lambda tokens: np.array(
            list(map(lambda x: np.mean(x, axis=0),
                embedder.transform_generator(tokens)))
        )

    merger = lambda column_values: np.concatenate(list(column_values), axis=-1)

    mapping = {
        'X': {
            'columns': {
                'premise_sparse_tfidf': {
                    'function': tfidf.sparse2dense,
                    'name': 'premise_tfidf'},
                'conclusion_sparse_tfidf': {
                    'function': tfidf.sparse2dense,
                    'name': 'conclusion_tfidf'},
                'tfidf_cosine_similarity': {},
                'premise_tokens': {
                    'function': mean_embedding,
                    'name': 'premise_mean_embedding'
                },
                'conclusion_tokens': {
                    'function': mean_embedding,
                    'name': 'conclusion_mean_embedding'
                },
            },
        },
        'y': {
            'columns': {
                'pro': {},
            },
        }
    }

    if merge_X:
        mapping['X']['merger'] = merger
    if merge_y:
        mapping['y']['merger'] = merger


    mapping = ml_ad.fill_mapping(mapping,
            default_transform = lambda x: x[:,None],
            before_transform = lambda x: x.values,
            after_transform = lambda x: x.astype(np.float32),
        )

    def complete_adaptor(data):
        data = ml_ad.apply_mapping(mapping, data)
        return data['X'], data['y']

    return complete_adaptor

