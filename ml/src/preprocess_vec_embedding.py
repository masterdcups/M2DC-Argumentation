import argparse
from pathlib import Path

import numpy as np
from tqdm import tqdm

def main(vec_path, output_path):
    vec_path = Path(vec_path)
    output_path = Path(output_path)

    tokens, matrix = vec2arrays(
            vec_path.open('r', encoding='utf-8'))

    np.savez(output_path,
            tokens = tokens, embeddings = matrix)


def vec2arrays(vec, oov_token='<OOV>'):
    """ Transforms a generator of .vec file lines into a tuple of numpy arrays: 
        (tokens, embedding_matrix).

    An extra row is added at index 0, for the Out-Of-Vocabulary token. It can be
    disabled by setting oov_token=None.
    """

    header = next(vec).split()
    nb_words, dimension = int(header[0]), int(header[1])

    if oov_token:
        nb_words += 1
    
    words = np.zeros(nb_words, dtype=np.dtype(str))
    embeddings = np.zeros((nb_words, dimension), dtype=np.float32)

    current_word_id = 0
    if oov_token:
        words[0] = oov_token
        current_word_id += 1
    
    for i, line in tqdm(enumerate(vec)):
        values = line.rstrip().split(' ')
        word, embedding = values[0], list(map(float, values[1:]))

        words[current_word_id] = word
        embeddings[current_word_id] = embedding

        current_word_id += 1

    return words, embeddings


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description=("Transforms a vec embedding file to a numpy archive" +
            "keyed by 'tokens' and 'embeddings'.")
        )
    argparser.add_argument(
            'vec_path',
            help='path to .vec embedding file',
        )
    argparser.add_argument(
            'output_path',
            help='path to save numpy archive (.npz) file',
        )
    args = argparser.parse_args()

    main(args.vec_path, args.output_path)
