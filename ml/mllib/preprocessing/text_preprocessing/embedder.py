import types

import numpy as np

class Embedder():
    """ Utility class built from a sequence of tokens and an embedding matrix.
        Can transform documents to their embedding matrix (generator-like), 
        or a whole corpus to its dense padded matrix.
        
        It uses the first embedding matrix row as the embedding for tokens
        not found in the dictionary. The tokens are mapped to the embedding
        vectors according to their index in the 'tokens' iterable (idx=0 -> row=0).
    """
    def __init__(self, tokens, embeddings, oov_vector=None):
        if len(tokens) != len(embeddings):
            raise ValueError(
                    ("{} tokens were passed, but the embedding matrix contains" +
                    " {} rows.").format(len(tokens), len(embeddings)))

        self.token2id = {
                token: i
                for i, token in enumerate(tokens)
            }

        self.embeddings = embeddings
        if oov_vector is not None:
            self.embeddings[0] = oov_vector

    def transform_generator(self, corpus):
        """ Tranforms a collection of documents into a generator of document
        embeddings. 
        """
        for document in corpus:
            embedding = self.embeddings[self.document2ids(document)]
            yield self.embeddings[self.document2ids(document)]

    def transform(self,
            corpus, 
            nb_documents = None,
            max_length = None,
            padding_value = -1.0, 
            document_position_offset = lambda doc_len, max_len: 0, # no offset
        ):
        """ Transforms an iterable of documents into a dense embedding matrix.
            Sequences (of embedding vectors) start at the index computed 
            by document_position_offset(), and are padded with padding_value.

            If nb_documents or max_length is None, it is computed in
            the function. If both are valued, the function can work on a
            generator.
        """
        if isinstance(corpus, types.GeneratorType):
            if nb_documents is None or max_length is None:
                raise ValueError(
                    "Cannot transform a corpus generator to a dense matrix " +
                    "without knowing dimensions in advance.")
        else:
            if nb_documents is None:
                nb_documents = len(corpus)
            if max_length is None:
                max_length = max(map(len, corpus))

        # Initialize the corpus embedding tensor.
        embeddings = np.full(
                (nb_documents, max_length, self.embeddings.shape[-1]), 
                padding_value, dtype=np.float32
            )

        # Fill the tensor.
        for i, token_ids in enumerate(map(self.document2ids, corpus)):
            document_length = len(token_ids)
            offset = document_position_offset(document_length, max_length)

            embeddings[i, offset:offset+document_length] = \
                    self.embeddings[token_ids]

        return embeddings


    def document2ids(self, document):
        ids = np.zeros(len(document), dtype=np.int32)
        for i, word in enumerate(document):
            ids[i] = self.token2id.get(word, 0)
        return ids
            


if __name__ == '__main__':
    vocabulary = ['<OOV>', 'dog', 'cat', 'horse', 'raddish']
    embeddings = np.array([
        [0.0, 0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0, 1.0],
        [2.0, 2.0, 2.0, 2.0],
        [3.0, 3.0, 3.0, 3.0],
        [4.0, 4.0, 4.0, 4.0],
    ])

    embedder = Embedder(vocabulary, embeddings)

    documents = [
        ['dog', 'dog', 'dog'],
        ['cat', 'dog', 'sad', 'dog'],
        ['horse', 'raddish', 'lol'],
        ['cat', 'raddish', '<OOV>', 'cat', 'cat', 'horse'],
        ['aeiou'],
    ]
    def document_generator(documents):
        for document in documents:
            yield document

    # document_position_offset most likely functions
    def left_padding(doc_len, max_len):
        return max([doc_len, max_len])-doc_len
    def right_padding(doc_len, max_len):
        return 0
    def center_padding(doc_len, max_len):
        return int(left_padding(doc_len, max_len)/2)

    embeddings = embedder.transform(
            #documents, 

            # instead of documents, we can use the generator with known dimensions
            #document_generator(documents),
            #nb_documents = len(documents), 
            #max_length = max(map(len, documents)),

            document_position_offset = center_padding,
            padding_value=-42.0
        )

    print(embeddings.shape)
    print(embeddings)
