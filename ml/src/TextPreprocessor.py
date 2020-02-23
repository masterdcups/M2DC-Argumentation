import operator

from mllib.AbstractTransformers import Transformer

import nltk
from mllib.preprocessing.text_preprocessing import text_preprocessing as text

class TextPreprocessor(Transformer):
    """ Transforms multiple text documents (str) into dictionary of text
    features.
    """

    def __init__(self, *kwargs):
        self.Lemmatizer = nltk.WordNetLemmatizer
        self.pos_tag_mapping = nltk.tag.mapping.tagset_mapping('en-ptb', 'universal')
        self.pos_tag2id = {
                pos_tag: i+3 # First three are <UNK>, <PAD> and <EOS>
                for i, pos_tag in
                enumerate(sorted(set(self.pos_tag_mapping.values())))
            }

    def transform(self, corpus, *kwargs):
        lemmatizer = self.Lemmatizer()

        for document in corpus:
            yield self._document2dict(document, lemmatizer)

    def _document2dict(self, document: str, lemmatizer: object) -> dict:
        """ Transforms a single document. """

        sentences_tokens = list(map(
                nltk.word_tokenize, 
                nltk.sent_tokenize(document)))

        sentences_spans = text.sentences_tokens2sentences_spans(sentences_tokens)

        tokens = [
            token.lower() 
            for sentence in sentences_tokens
            for token in sentence
        ]

        pos_tags = list(map(
                lambda tag: self.pos_tag_mapping[operator.itemgetter(1)], 
                nltk.tag.pos_tag(tokens)))
        pos_tags_ids = list(map(lambda tag: self.pos_tag2id[tag], pos_tags))

        lemmas = [
            lemmatizer.lemmatize(
                token)#, text.PennTreebank_to_WordNet(pos_tag))
            for token, pos_tag in zip(tokens, pos_tags)
        ]

        return {
            'document': document,
            'sentences_spans': sentences_spans,
            'tokens': tokens,
            'pos_tags': pos_tags,
            'pos_tags_ids': pos_tags_ids,
            'lemmas': lemmas,
        }
