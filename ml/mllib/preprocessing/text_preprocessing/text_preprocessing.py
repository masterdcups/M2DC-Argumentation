import sys
import operator

import typing

import pickle as pkl
import nltk
import gensim

from mllib.preprocessing.dataset_preparation import utils

#def document2sentences_tokens(document: str) -> [[str]]:
#    return list(map(nltk.word_tokenize, nltk.sent_tokenize(document)))

def sentences_tokens2sentences_spans(sentences_tokens: [[str]]) -> [(int, int)]:
    sentences_spans = []

    current_token_index = 0
    for sentence in sentences_tokens:
        sentence_len = len(sentence)
        sentences_spans.append(
            (current_token_index, current_token_index+sentence_len-1))
        current_token_index += sentence_len

    return sentences_spans

def sentences_tokens2tokens(sentences_tokens: [[str]]) -> [str]:
    return [
        token for sentence in sentences_tokens for token in sentence
    ]

def tokens2pos_tags(tokens: [str]) -> [str]:
    return list(map(operator.itemgetter(1), nltk.tag.pos_tag(tokens)))


def tokens2lemmas(
        tokens: [str], 
        lemmatize, # function to apply to each token, can take pos_tags as arg
        pos_tags: [str] = None
    ) -> [str]:

    if not pos_tags:
        return [lemmatize(token.lower()) for token in tokens]
    else:
        return [
            lemmatize(token.lower(), PennTreebank_to_WordNet(pos_tag))
            for token, pos_tag in zip(tokens, pos_tags)
        ]

def PennTreebank_to_WordNet(pos_tag: str) -> str:
    """
        Translates Penn Treebank PoS tags to WordNet PoS tags.
    """

    prefix = pos_tag[:1]

    if prefix == 'V':
        return nltk.corpus.wordnet.VERB
    if prefix == 'R':
        return nltk.corpus.wordnet.ADV
    if prefix == 'J':
        return nltk.corpus.wordnet.ADJ

    return nltk.corpus.wordnet.NOUN

# Might break if we use a lemmatizer other than the WordNet one.
def make_lemmatize(lemmatizer: object = None):
    """ Returns a function lemmatizing a token, optionally with its pos_tag. """

    if not lemmatizer:
        lemmatizer = nltk.stem.WordNetLemmatizer()
    # Closure for lemmatizer
    def lemmatize(lemmatizer):
        lemmatizer_reference = lemmatizer

        return lemmatizer_reference.lemmatize

    return lemmatize(lemmatizer) 

def preprocessed_node_generator(
        node_generator_getter, 
        lemmatizer = None,
        verbose = False,
    ):
    """
        Preprocessing procedure for nodes of the form {
            's': "woof woof",
            'n': 42,
            'debate_name': "Is bad good?"
        }.
        It produces a generator, which contains dictionary for each node, with
        entries being non corpus specific (no fitting of models, prefitted like
        nltk.pos_tags (trained on PennTreeband) are used) nlp transformations, 
        which currently are:
            - sentence_spans
            - tokens
            - pos_tags
            - lemmas
        plus the initial key/value pairs.
    """

    lemmatize = make_lemmatize(nltk.stem.WordNetLemmatizer())

    nodes = node_generator_getter()

    for node in nodes:
        document = node['s']        
        document_id = node['n']
        document_debate_name = node['debate_name']
        
        sentences_tokens = document2sentences_tokens(document)
        sentences_spans = sentences_tokens2sentences_spans(sentences_tokens)
        tokens = sentences_tokens2tokens(sentences_tokens)
        pos_tags = tokens2pos_tags(tokens)
        lemmas = tokens2lemmas(
                tokens, lemmatize, map(PennTreebank_to_WordNet, pos_tags))

        yield {
            'id': document_id,
            'debate_name': document_debate_name,
            'document': document,
            'sentences_spans': sentences_spans,
            'tokens': tokens,
            'pos_tags': pos_tags,
            'lemmas': lemmas,
        }



def fit_dictionary(nodes_nlp_generator_getter, 
        parameters,
        verbose = False):

    if verbose:
        print("Fitting dictionary.")

    dictionary = gensim.corpora.Dictionary(map(
        lambda node: [lemma for lemma in node['lemmas'] if lemma.isalpha()],
        nodes_nlp_generator_getter()))

    if verbose:
        print("\tParsed {} documents.".format(dictionary.num_docs))
        print("\tFound {} unique tokens.".format(dictionary.num_pos))
        print("\t{} non zero entries.".format(dictionary.num_nnz), 
                "({}/{} = {:.3f})".format(
                    dictionary.num_nnz, dictionary.num_pos,
                    dictionary.num_nnz / dictionary.num_pos))

    kept_tokens = ['not', 'for', 'against', 'good', 'bad']
    dictionary.filter_extremes(
            no_below=parameters['min_frequency_absolute'], 
            no_above=parameters['max_frequency_relative'],
            keep_n=parameters['vocabulary_size'], 
            keep_tokens=kept_tokens)

    # Transforms dictionary indices into contiguous range [0 (1?), |Vocabulary|]
    dictionary.compactify()

    return dictionary


def fit_tfidf(
        nodes_nlp_generator_getter, 
        dictionary = None,
        verbose = False,
    ):
    """
        Fits nlp models to node document lemmas.
    """

    if not dictionary:
        if verbose:
            print("Fitting dictionary in fit_tfidf().")
        dictionary = fit_dictionary(nodes_nlp_generator_getter, verbose=verbose)

    # technically node2bag-of-lemmas
    def node2bow(node):
        return dictionary.doc2bow(node['lemmas'])

    if verbose:
        print("Fitting Tf-Idf model.")

    tfidf = gensim.models.TfidfModel(
            map(node2bow, nodes_nlp_generator_getter()), 
            normalize=True)

    return tfidf



if __name__ == '__main__':

    dummy_node_generator_getter = lambda : (
        {'s': "I am John. I like pies.", 'n': 1, 
        'debate_name': "Geopolitical situation in the middle east is fine."},
        {'s': "Pies are quite meh. Bananas are good though.", 'n': 2, 
        'debate_name': "Geopolitical situation in the middle east is fine."},
        {'s': "Arguments are good.", 'n': 3, 
        'debate_name': "Geopolitical situation in the middle east is fine."},
    )

    for x in preprocessed_node_generator(dummy_node_generator_getter):
        print(*x.items(), sep='\n')
        print()


    #node_nlp_generator = preprocess_nodes_nlp(lambda : utils.load(sys.argv[1]))
    #output_dir = sys.argv[2]

    #nodes_nlp_filename = "{}/nodes_nlp.pkl".format(output_dir)
    #utils.dump(node_nlp_generator, nodes_nlp_filename)

    #dictionary = fit_dictionary(
    #    lambda : utils.load(nodes_nlp_filename), verbose = True
    #)
    #pkl.dump(dictionary, open("{}/dictionary.pkl".format(output_dir), 'wb'))

    #tfidf = fit_tfidf(
    #    lambda : utils.load(nodes_nlp_filename),
    #    dictionary = dictionary,
    #    verbose = True
    #)
    #pkl.dump(tfidf, open("{}/tfidf.pkl".format(output_dir), 'wb'))



    
