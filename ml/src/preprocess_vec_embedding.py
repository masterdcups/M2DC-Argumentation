import argparse
from pathlib import Path
import re

import numpy as np
from sklearn.decomposition import PCA
from tqdm import tqdm

def main(vec_path, output_path):
    vec_path = Path(vec_path)
    output_path = Path(output_path)

    tokens, matrix = vec2arrays(
            vec_path.open('r', encoding='utf-8'), reduce_dim=50)

    np.savez(output_path,
            tokens = tokens, embeddings = matrix)


def vec2arrays(
        vec, 
        oov_token='<UNK>', # 0.0 vector
        pad_token='<PAD>', # -1.0 norm vector
        eos_token='<EOS>', # 1.0 norm vector
        reduce_dim=None, # PCA if valued
    ):
    """ Transforms a generator of .vec file lines into a tuple of numpy arrays: 
        (tokens, embedding_matrix).

    An extra row is added at index 0, for the Out-Of-Vocabulary token. It can be
    disabled by setting oov_token=None. Same for padding (next index) and
    End-Of-Sequence (next index) tokens.
    """

    # Regex pattern matching words to exclude from the embeddings
    pattern = re.compile(r'<.*>')

    
    # if header contains vocab_size, dimensionality
    header = next(vec).split()
    nb_words, dimension = int(header[0]), int(header[1])

    # else
    #nb_words, dimension = 100000, 50

    if oov_token:
        nb_words += 1
    if pad_token:
        nb_words += 1
    if eos_token:
        nb_words += 1
    
    words = np.zeros(nb_words, dtype=np.dtype(object))
    embeddings = np.zeros((nb_words, dimension), dtype=np.float32)

    current_word_id = 0

    if oov_token:
        words[current_word_id] = oov_token
        current_word_id += 1

    if pad_token:
        words[current_word_id] = pad_token
        embeddings[current_word_id] = -1.0 * np.sqrt(1.0 / dimension)
        current_word_id += 1

    if eos_token:
        words[current_word_id] = eos_token
        embeddings[current_word_id] = 1.0 * np.sqrt(1.0 / dimension)
        current_word_id += 1
    
    for i, line in tqdm(enumerate(vec)):
        values = line.rstrip().split(' ')
        word, embedding = values[0], map(float, values[1:])

        if pattern.match(word):
            continue

        words[current_word_id] = word
        embeddings[current_word_id] = list(embedding)

        current_word_id += 1

        if current_word_id >= nb_words:
            break

    if reduce_dim and dimension > reduce_dim:
        pca = PCA(reduce_dim, copy=False)
        embeddings = pca.fit_transform(embeddings)


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
