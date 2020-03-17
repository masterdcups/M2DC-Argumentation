import numpy as np

from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad

def Adaptor(
        tfidf, embedder,
        merge_X=False, merge_y=False
    ):
    """ Maps a preprocessed arguments DataFrame columns to a dictionary
    of np.array keyed by ['X'|'y'], followed by ['name'] if the columns
    were not merged (merge_X and merge_y).
    """
    def documents2tensor(documents):
        def left_padding(doc_len, max_len):
            return max([doc_len, max_len])-doc_len

        return embedder.transform(documents,
                document_position_offset=left_padding)

    merger = lambda column_values: np.concatenate(list(column_values), axis=-1)

    mapping = {
        'X': {
            'columns': {
                'premise_tokens': {
                    'function': documents2tensor,
                    'name': 'premise_embeddings'
                },
                'conclusion_tokens': {
                    'function': documents2tensor,
                    'name': 'conclusion_embeddings'
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

