import numpy as np
import gensim

from mllib.AbstractTransformers import Transformer

class TfIdf(Transformer):
    def __init__(self):
        pass

    def fit(self, dictionary):
        self.tfidf = gensim.models.TfidfModel(
                dictionary = dictionary)

        self.vocabulary_size = len(dictionary.token2id)

    def transform(self, bags_of_words, dense=False, dense_dtype=np.float32):
        if not dense:
            return [vec for vec in self.tfidf[bags_of_words]]
        else:
            return self.sparse2dense(
                    self.tfidf[bags_of_words],
                    dense_dtype)

    def sparse2dense(self, sparse_vectors, dtype=np.float32):
        return gensim.matutils.corpus2dense(
                sparse_vectors, self.vocabulary_size).T

