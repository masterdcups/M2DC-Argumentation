import abc
import pickle as pkl

""" Abstract Transformer class
    
    Inspired by sklearn transformers, defines fit(), transform(), fit_transform(),
    save() and load() (load is a class method).
"""

class Transformer(abc.ABC):
    def __init__(self, *kwargs):
        pass

    def fit(self, X, y=None, *kwargs):
        pass

    @abc.abstractmethod
    def transform(self, X, *kwargs):
        pass

    def fit_transform(self, X, y=None, *kwargs):
        self.fit(X, y, *kwargs)
        return self.transform(X, *kwargs)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pkl.dump(self, f)

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as f:
            return pkl.load(f)
