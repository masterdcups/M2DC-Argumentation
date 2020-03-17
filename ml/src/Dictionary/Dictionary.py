import gensim

from mllib.AbstractTransformers import Transformer

class Dictionary(Transformer):
    def __init__(self):
        pass

    def fit(self, corpus,
            min_frequency_absolute = 5, 
            max_frequency_relative = 0.5,
            vocabulary_size = 1000,
            kept_tokens = [],
        ):

        self.vocabulary_size = 1000
        self.dictionary = gensim.corpora.Dictionary(corpus)
        self.dictionary.filter_extremes(
                no_below=min_frequency_absolute,
                no_above=max_frequency_relative,
                keep_n=vocabulary_size,
                keep_tokens=kept_tokens)

        self.dictionary.compactify()


    def transform(self, corpus):
        return (self.dictionary.doc2bow(document) for document in corpus)

