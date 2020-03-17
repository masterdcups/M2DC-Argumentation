import numpy as np
import keras

from keras.layers import Input
from keras.layers import Embedding
from keras.layers import LSTM
from keras.layers import Bidirectional
from keras.layers import concatenate, add, dot

from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras.optimizers import Adam


from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad



def getOptionsCocarascu():
    default_options = dict()
    default_options["embedded_size"] = 100
    default_options["vocab_size"] = 50
    default_options["maxlen"] = 50
    default_options["train_embedding"] = False
    default_options["embedding_matrix"] = None
    default_options["n_lstm"] = 32
    default_options["acti_lstm"] = "relu"
    default_options["lstm"] = "bi"
    default_options["dropout_rate"] = 0.2
    default_options["merge"] = "concat"
    default_options["n_nn"] = 32
    default_options["n_classif"] = 2#2, change to 1 because of input shape (and also sparse_cateorical_crossentropy)
    default_options["lrate"] = 0.001

    return default_options


def Model(input_layers, output_layer, 
        embedded_size = None,
        vocab_size = None,
        embedding_matrix = None,
        #maxlen = 50,
        train_embedding = False,
        n_lstm = 32,
        acti_lstm = 'relu',
        lstm = 'bi',
        dropout_rate = 0.2,
        merge = 'concat',
        n_nn = 32,
        n_classif = 1,
        lrate = 0.001,
        **kwargs
    ):
    """
    Deep Learning model from Cocarascu-Toni paper:
    "Identifying attack and support argumentative relations using deep learning".
    It implements a two LSTM network (uni or bi directional) to predict the 
    relation between two arguments.
    
    Architecture:
    argA -> embedding -> lstm -> dropout |
                                         merge -> dense -> softmax
    argB -> embedding -> lstm -> dropout |
    
    Input: 
        options => dict(). Keys:
            embedded_size => output dimension of embeddings. Integer
            vocab_size => vocabulary size (total number of attributes). Integer
            maxlen => Max. Length of input text (sequences size). Integer
            train_embedding => To continue training embedding or not. Boolean
            embedding_matrix => Embedding from pre-trained set (eg. GloVo). Matrix
            lstm => Set Unidirectional ("uni") or Bidirectional ("bi") LSTM. String
            n_lstm => Output size of LSTM. Integer (values: 32,64,100,128)
            acti_lstm => Activation for LSTM. String
            dropout_rate => Rate for final dropout layer of individual model. Float
            merge => Merge by concatenation "concat" or sum "add"
            n_nn => Number of nodes from final hidden Dense layer. Integer
            n_classif => Number of nodes from output layer. Defaul 3.  Integer
            lrate => Learning rate. Float
    Returns:
        model => keras.model
    """
   
    #default_options = getOptionsCocarascu()
    #if options is None:
    #    options = default_options
    #else:
    #    default_options.update(options)
    #    options = default_options
    #
    ##maxlen = default_options["maxlen"]
    #embedded_size = default_options["embedded_size"] 
    #max_features = default_options["vocab_size"] 
    #embedding_matrix = default_options["embedding_matrix"]
    
    #argA = Input(shape=(maxlen,))
    #argB = Input(shape=(maxlen,))
    argA = input_layers['premise_seq']
    argB = input_layers['conclusion_seq']

    word_embedding = Embedding(
            vocab_size, embedded_size,
            weights = [embedding_matrix],
            trainable = train_embedding,
        )

    pos_tagsA = input_layers['premise_pos_tags_ids']
    pos_tagsB = input_layers['conclusion_pos_tags_ids']
    pos_tag_embedding = Embedding(
            16, 4,
            embeddings_constraint = keras.constraints.MaxNorm(
                4.0 / embedded_size, axis=-1)
        )

    
    #Model for arg1
    #x = Embedding(
    #        vocab_size,
    #        embedded_size, 
    #        weights=embedding_matrix, 
    #        #trainable=train_embedding
    #    )(argA)

    #x = word_embedding(argA)
    x = concatenate([word_embedding(argA), pos_tag_embedding(pos_tagsA)])

    if lstm == "bi":
        x = Bidirectional(LSTM(n_lstm, 
                           activation=acti_lstm,
                           return_sequences=False))(x) 
    else:
        x = LSTM(n_lstm, 
                 activation=acti_lstm,
                 return_sequences=False)(x) 
        
    x = Dropout(rate=dropout_rate)(x)
    x = keras.models.Model(inputs=[argA, pos_tagsA], outputs=x)
    #x = keras.models.Model(inputs=argA, outputs=x)
    
    #Model for arg2
    #y = Embedding(vocab_size,
    #              embedded_size, 
    #              weights=embedding_matrix, 
    #              trainable=train_embedding)(argB)

    #y = word_embedding(argB)
    y = concatenate([word_embedding(argB), pos_tag_embedding(pos_tagsB)])
    if lstm == "bi":
        y = Bidirectional(LSTM(n_lstm, 
                           activation=acti_lstm,
                           return_sequences=False))(y) 
    else:
        y = LSTM(n_lstm, 
                 activation=acti_lstm,
                 return_sequences=False)(y) 
    y = Dropout(rate=dropout_rate)(y)
    #y = keras.models.Model(inputs=argB, outputs=y)
    y = keras.models.Model(inputs=[argB, pos_tagsB], outputs=y)

    #Merge models
    if merge == "concat":
        combined = concatenate([x.output, y.output])
    elif merge == "sum":
        combined = add([x.output, y.output])
    
    z = Dense(n_nn, activation="relu")(combined) 

    #z = Dense(n_classif, activation="softmax")(z)
    z = Dense(n_classif, activation="sigmoid")(z)

    z = output_layer(z)
    model = keras.models.Model(inputs=[*x.input, *y.input], outputs=z)
    
    adam = Adam(lr=lrate)
    #model.compile(optimizer=adam, loss="categorical_crossentropy", metrics=["accuracy"])

    #model.compile(optimizer=adam, loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.compile(optimizer=adam, loss="binary_crossentropy", metrics=["binary_accuracy"])
    
    return model


def ModelCfg(**kwargs):
    return {
        #'maxlen': 50,
        'train_embedding': False,
        #'embedding_matrix': None,
        'n_lstm': 32,
        'acti_lstm': 'relu',
        'lstm': 'bi',
        'dropout_rate': 0.2,
        'merge': 'concat',
        'n_nn': 16,
        'n_classif': 1,
        'lrate': 0.001,
    }


def FitCfg(**kwargs):
    return {
        'batch_size': 64,
        'steps_per_epoch': 50,
        'epochs': 20,
    }


def Adaptor(
        token2id,
        maxlen = 50,
        **kwargs,
    ):

    def documents2ids(documents):
        # Take the last maxlen-1 tokens, pre-padded with <PAD> if needed
        def pad(documents):
            return keras.preprocessing.sequence.pad_sequences(
                    documents,
                    padding='pre', value=token2id['<PAD>'],
                    truncating='pre', maxlen=maxlen-1,
                    dtype=np.int32
                )
        # Convert to tokens
        documents = list(map(
                lambda document: list(map(
                    lambda token: token2id.get(token,0), 
                    document)), 
                documents))

        #for document in documents:
        #    document = np.array(
        #            list(map(lambda token: token2id.get(token,0), document)), 
        #            dtype=np.int32
        #        )
        #print(documents)
        # Pad / trim (might want to do before conversion to tokens)
        documents = pad(documents)

        # Add <EOS> at the end
        documents = np.concatenate([
                documents, np.full(
                    (len(documents), 1), token2id['<EOS>'], dtype=np.int32)
            ], axis=-1)

        return documents

    def pad_tags(tags):
        tags = keras.preprocessing.sequence.pad_sequences(tags,
                padding='pre', value=1,
                truncating='pre', maxlen=maxlen-1,
                dtype=np.int32)
        tags = np.concatenate([
                tags, np.full((len(tags), 1), 2, dtype=np.int32)
            ], axis=-1)
        return tags


    #return keras.preprocessing.sequence.pad_sequences(
    #        list(map(
    #            lambda document: list(map(
    #                lambda token: token2id.get(token, 0),
    #                document)),
    #            documents)),
    #        maxlen=maxlen)

    merger = lambda column_values: np.concatenate(list(column_values), axis=-1)

    mapping = {
        'X': {
            'columns': {
                'premise_tokens': {
                    'function': documents2ids,
                    'name': 'premise_seq'
                },
                'conclusion_tokens': {
                    'function': documents2ids,
                    'name': 'conclusion_seq'
                },
                'premise_pos_tags_ids': {
                    'function': pad_tags,
                    'name': 'premise_pos_tags_ids'
                },
                'conclusion_pos_tags_ids': {
                    'function': pad_tags,
                    'name': 'conclusion_pos_tags_ids'
                },
            },
        },
        'y': {
            'columns': {
                'pro': {},
            },
            'merger': merger,
        }
    }


    mapping = ml_ad.fill_mapping(mapping,
            default_transform = lambda x: x[:,None],
            before_transform = lambda x: x.values,
        )

    def complete_adaptor(data):
        data = ml_ad.apply_mapping(mapping, data)
        return data['X'], data['y']

    return complete_adaptor



