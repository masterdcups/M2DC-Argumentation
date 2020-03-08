import numpy as np
import keras
import keras.backend as K
import tensorflow as tf

from keras.layers import (
        Input, Embedding,
        Reshape, RepeatVector,Flatten,
        Concatenate, Add, Subtract, Multiply, Dot, 
        Dense, Lambda,
        RNN, GRU, LSTM, Conv1D, 
        MaxPooling1D, AveragePooling1D, 
        GlobalMaxPooling1D, GlobalAveragePooling1D,
        Activation, LeakyReLU, Softmax,
        Bidirectional,
        Dropout, BatchNormalization, SpatialDropout1D, GaussianNoise
    )
from keras.optimizers import Adam

from mllib.preprocessing.ml_preprocessing import ml_adaptors as ml_ad


def Model(input_layers, output_layer, 
        word_matrix,
        sentiment_matrix,
        train_sentiment = False,
        embedding_noise_std = 0.01,
        embedding_projection_dimension = 64,
        dropout_rate = 0.2,
        recurrent_dropout_rate = 0.0,
        convolution_droupout_rate = 0.1,
        attention_dropout_rate = 0.1,
        nb_encoders = 1,
        nb_decoders = 2,
        nb_attention_heads = 2,
        optimizer = Adam(1e-3),
        **kwargs
    ):

    # Remove second to last axis of tensor after embedding tokens
    def embedding_squeezer(embedding_layer):
        def squeezer(rank4tensor):
            return K.squeeze(rank4tensor, axis=2)
        return Lambda(lambda ids: squeezer(embedding_layer(ids)))
   
    embedding_squeezer = Lambda(lambda tensor: K.squeeze(tensor, axis=-2),
            name='Squeezer_axis_-2')

    # Word embeddings
    premise_word_ids = input_layers['premise_word_ids']
    conclusion_word_ids = input_layers['conclusion_word_ids']

    word_embedding = Embedding(
            *word_matrix.shape,
            weights = [word_matrix],
            trainable = False,
        )

    premise_word_embeddings = embedding_squeezer(
            word_embedding(premise_word_ids))
    conclusion_word_embeddings = embedding_squeezer(
            word_embedding(conclusion_word_ids))

    # Apply gaussian noise
    word_embedding_noise = GaussianNoise(embedding_noise_std)
    premise_word_embeddings = word_embedding_noise(premise_word_embeddings)
    conclusion_word_embeddings = word_embedding_noise(conclusion_word_embeddings)

    # Drop dimensions
    #word_embedding_spatial_dropout = SpatialDropout1D(0.1)
    #premise_word_embeddings = word_embedding_spatial_dropout(
    #        premise_word_embeddings)
    #conclusion_word_embeddings = word_embedding_spatial_dropout(
    #        conclusion_word_embeddings)

    # PoS embeddings
    premise_pos_tag_ids = input_layers['premise_pos_tags_ids']
    conclusion_pos_tag_ids = input_layers['conclusion_pos_tags_ids']

    pos_tag_embedding = Embedding(
            16, 4,
            trainable=True,
            embeddings_constraint = keras.constraints.UnitNorm(axis=-1)
        )
    premise_pos_tag_embeddings = embedding_squeezer(
            pos_tag_embedding(premise_pos_tag_ids))
    conclusion_pos_tag_embeddings = embedding_squeezer(
            pos_tag_embedding(conclusion_pos_tag_ids))

    # Sentiment embeddings
    premise_sentiment_ids = input_layers['premise_sentiment_ids']
    conclusion_sentiment_ids = input_layers['conclusion_sentiment_ids']

    sentiment_embedding = Embedding(
            *sentiment_matrix.shape,
            weights = [sentiment_matrix],
            trainable = train_sentiment,
            embeddings_constraint = (
                    keras.constraints.MinMaxNorm(axis=-1) 
                    if train_sentiment else None
                )
            )
    premise_sentiment_embeddings = embedding_squeezer(
            sentiment_embedding(premise_sentiment_ids))
    conclusion_sentiment_embeddings = embedding_squeezer(
            sentiment_embedding(conclusion_sentiment_ids))


    inputs = [
            premise_word_ids, conclusion_word_ids,
            premise_pos_tag_ids, conclusion_pos_tag_ids,
            premise_sentiment_ids, conclusion_sentiment_ids,
        ]


    premise_embeddings = Concatenate()([
            premise_word_embeddings, 
            premise_pos_tag_embeddings, 
            premise_sentiment_embeddings,
        ])
    conclusion_embeddings = Concatenate()([
            conclusion_word_embeddings, 
            conclusion_pos_tag_embeddings, 
            conclusion_sentiment_embeddings,
        ])
    dense_embeddings = Dense(embedding_projection_dimension)
    premise_embeddings = dense_embeddings(premise_embeddings)
    conclusion_embeddings = dense_embeddings(conclusion_embeddings)
    sequence_shape = K.int_shape(premise_embeddings)[-2:]

    def tile2sequence(args):
        return RepeatVector(K.shape(args[1])[-2])(args[0])


    def EncoderDecoder(sequence_shape, units = 8):
        input_encode = Input(shape=sequence_shape[-2:])
        input_decode = Input(shape=sequence_shape[-2:])

        sequence_to_encode = input_encode
        sequence_to_decode = input_decode

        recurrent_layer = LSTM
        
        encoding = sequence_to_encode
        decoding = sequence_to_decode

        encoding = Bidirectional(
                recurrent_layer(
                    units, 
                    return_sequences=False, 
                    return_state=True,
                    recurrent_dropout=recurrent_dropout_rate),
                merge_mode='concat')(encoding)

        decoding = Bidirectional(
                recurrent_layer(units, return_sequences=False,
                    recurrent_dropout=recurrent_dropout_rate),
                merge_mode='concat')(
                        decoding,
                        initial_state=encoding[1:])

        return keras.models.Model(
                inputs=[sequence_to_encode, sequence_to_decode],
                outputs=decoding) 

    def CNN(sequence_shape, units = 32):
        input_sequence = Input(shape=sequence_shape[-2:])
        conv_act = 'relu'

        sequence = Dense(units, activation='relu')(input_sequence) 

        conv_1 = Conv1D(units, 3, 
                activation=conv_act
            )(sequence)
        conv_1 = SpatialDropout1D(convolution_droupout_rate)(conv_1)

        conv_2 = Conv1D(units, 3, dilation_rate=2,
                activation=conv_act
            )(conv_1)
        
        conv_3 = Conv1D(units, 3, dilation_rate=4,
                activation=conv_act
            )(conv_2)


        return keras.models.Model(
                inputs=input_sequence, 
                outputs=[conv_1, conv_2, conv_3])

    
    #cnn = CNN(sequence_shape[-2:], sequence_shape[-1])
    #conclusion_convolutions = cnn(conclusion_embeddings)
    #premise_convolutions = cnn(premise_embeddings)

    rnn = EncoderDecoder(sequence_shape[-2:], 16)
    rnn.name = 'Encoder-Decoder'
                

    #cnn = CNN(sequence_shape[-2:], sequence_shape[-1])
    #dense_cnn_encoding = Dense(sequence_shape[-1], activation='relu')

    rnn_conclusion_encoding = rnn([premise_embeddings, conclusion_embeddings])
    rnn_premise_encoding = rnn([conclusion_embeddings, premise_embeddings])

    #dense_rnn_encoding = Dense(sequence_shape[-1], activation='relu')
    #rnn_conclusion_encoding = dense_rnn_encoding(rnn_conclusion_encoding)
    #rnn_premise_encoding = dense_rnn_encoding(rnn_premise_encoding)

    #conclusion_convolutions = cnn(conclusion_embeddings)
    #premise_convolutions = cnn(premise_embeddings)

    #cnn_conclusion_encoding = Concatenate()([
    #        GlobalAveragePooling1D()(conclusion_convolutions[0]),
    #        GlobalMaxPooling1D()(conclusion_convolutions[0]),
    #        GlobalAveragePooling1D()(conclusion_convolutions[1]),
    #        GlobalMaxPooling1D()(conclusion_convolutions[1]),
    #        GlobalAveragePooling1D()(conclusion_convolutions[2]),
    #        GlobalMaxPooling1D()(conclusion_convolutions[2]),
    #    ])

    #cnn_premise_encoding = Concatenate()([
    #        GlobalAveragePooling1D()(premise_convolutions[0]),
    #        GlobalMaxPooling1D()(premise_convolutions[0]),
    #        GlobalAveragePooling1D()(premise_convolutions[1]),
    #        GlobalMaxPooling1D()(premise_convolutions[1]),
    #        GlobalAveragePooling1D()(premise_convolutions[2]),
    #        GlobalMaxPooling1D()(premise_convolutions[2]),
    #    ])


    #cnn_conclusion_encoding = dense_cnn_encoding(cnn_conclusion_encoding)
    #cnn_premise_encoding = dense_cnn_encoding(cnn_premise_encoding)


    argument = Concatenate()([
            rnn_conclusion_encoding, rnn_premise_encoding,
            Subtract()([rnn_conclusion_encoding, rnn_premise_encoding]),
            Multiply()([rnn_conclusion_encoding, rnn_premise_encoding]),
        ])

    argument = Dense(16, activation='relu')(argument)
    argument = Dropout(dropout_rate)(argument)

    argument = Dense(8, activation='relu')(argument)

    pro = Dense(1, activation="sigmoid")(argument)
    pro = output_layer(pro)

    model = keras.models.Model(inputs=inputs, outputs=pro,
            name="RNN-Small")
    
    model.compile(
        optimizer=optimizer, 
        loss="binary_crossentropy", 
        metrics=["binary_accuracy"],
    )
    
    return model



def ModelCfg(**kwargs):
    return {
        'train_sentiment': False,
        'embedding_projection_dimension': 16,
        'embedding_noise_std': 0.001,
        'dropout_rate': 0.5,

        # Transformer/attention parameters
        'attention_dropout_rate': 0.1,
        'nb_attention_heads': 4,
        'nb_encoders': 2,
        'nb_decoders': 6,
        # CNN parameters
        'convolution_droupout_rate': 0.5,
        # RNN parameters
        'recurrent_dropout_rate': 0.0,

        'optimizer': keras.optimizers.Adam(
                #clipvalue=0.25,
                learning_rate = 5e-3
            )
    }


def FitCfg(**kwargs):
    steps = 128
    epochs = 20
    return {
        'batch_size': 64,
        'steps_per_epoch': steps,
        'epochs': epochs,
        'callbacks': [
                #keras.callbacks.ReduceLROnPlateau(
                WarmupReduceLROnPlateau(
                    initial_lr=5e-4, base_lr=5e-3, warmup_steps=steps,
                    monitor='loss', factor=0.63, patience=5,
                    min_delta=0.01, min_lr=5e-4,
                ),
            ],

    }


def Adaptor(
        word_embedding_dictionary,
        sentiment_embedding_dictionary,
        maxlen = 50,
        augmentation_rate = None,
        **kwargs,
    ):

    # Trim, augment and pad document token ids
    def pad(documents, value, dtype=np.int32):
        def trim(document):
            l = len(document)
            
            # Augment
            if augmentation_rate is not None:
                for i in range(int(np.floor(augmentation_rate*l))):
                    swap = np.random.randint(0, l-1, 2)
                    document[swap[0]], document[swap[1]] = \
                            document[swap[1]], document[swap[0]] 

                to_delete = np.random.randint(
                        0, l-1, int(np.floor(augmentation_rate*l)))
                np.delete(document, to_delete)

            if l < maxlen:
                return document

            # Trim
            first = int(np.floor((maxlen-1)/2))
            second = min(((maxlen-1)-first), l-first)
            return np.concatenate([
                document[:first], document[-second:]
            ])

        def pad_offset(doc_len):
            return (max(doc_len, maxlen)-doc_len)//2
            
        padded = np.full((len(documents), maxlen-1), value, dtype=np.int32)
        for i, document in enumerate(documents):
            doc = trim(document)
            doc_len = len(doc)
            offset = pad_offset(doc_len) 
            padded[i, offset:offset+doc_len] = doc

        return padded


    def append(documents, value, dtype=np.int32):
        return np.concatenate([
                documents, np.full(
                    (len(documents), 1), value, dtype=dtype)
            ], axis=-1)

    def documents2ids(documents, dictionary):
        return list(map(
                lambda document: list(map(
                    lambda token: dictionary.get(token,0), 
                    document)), 
                documents))

    def prepare_documents(documents):
        documents = documents2ids(documents, word_embedding_dictionary)
        documents = pad(documents, 1)
        documents = append(documents, 2)
        return documents[:,:,None]

    def prepare_pos_tags(tags):
        tags = pad(tags, 1)
        tags = append(tags, 2)
        return tags[:,:,None]

    def prepare_sentiments(documents):
        sentiments = documents2ids(documents, sentiment_embedding_dictionary)
        sentiments = pad(sentiments, 1)
        sentiments = append(sentiments, 2)
        return sentiments[:,:,None]

    merger = lambda column_values: np.concatenate(list(column_values), axis=-1)

    mapping = {
        'X': {
            'streams': {
                'premise_word_ids': {
                    'function': prepare_documents,
                    'column': 'premise_tokens'
                },
                'conclusion_word_ids': {
                    'function': prepare_documents,
                    'column': 'conclusion_tokens'
                },
                'premise_pos_tags_ids': {
                    'function': prepare_pos_tags,
                    'column': 'premise_pos_tags_ids'
                },
                'conclusion_pos_tags_ids': {
                    'function': prepare_pos_tags,
                    'column': 'conclusion_pos_tags_ids'
                },
                'premise_sentiment_ids': {
                    'function': prepare_sentiments,
                    'column': 'premise_lemmas'
                },
                'conclusion_sentiment_ids': {
                    'function': prepare_sentiments,
                    'column': 'conclusion_lemmas'
                },
            },
        },
        'y': {
            'streams': {
                'pro': {},
            },
            'merger': merger,
        }
    }


    mapping = ml_ad.fill_mapping(mapping,
            default_transform = lambda x: x[:,None],
            before_transform = lambda x: x.values,
        )

    # Uncomment for some debug prints
    #for part in mapping:
    #    print(part)
    #    for stream in part:
    #        print('\t', stream)

    def complete_adaptor(data):
        data = ml_ad.apply_mapping(mapping, data)
        return data['X'], data['y']

    return complete_adaptor

# Linear increase of the learning rate for warmup_steps steps, then classic
# ReduceLROnPlateau.
class WarmupReduceLROnPlateau(keras.callbacks.ReduceLROnPlateau):
    def __init__(self, warmup_steps, initial_lr=1e-4, base_lr=1e-3, **kwargs):
        super().__init__(**kwargs)
        self.warmup_steps = warmup_steps

        if initial_lr > base_lr:
            warnings.warn(
                'Warmup initial LR (%s) is greater than base LR (%s).'
                'Defaulting to base LR for the whole warmup.' % 
                (initial_lr, base_lr), RuntimeWarning
            )
            initial_lr = base_lr

        self.initial_lr = initial_lr
        self.base_lr = base_lr

    def on_train_begin(self, logs=None):
        self._reset()
        self.completed_warmup_steps = 0
        K.set_value(self.model.optimizer.lr, self.initial_lr)

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs['lr'] = K.get_value(self.model.optimizer.lr)
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn(
                'Reduce LR on plateau conditioned on metric `%s` '
                'which is not available. Available metrics are: %s' %
                (self.monitor, ','.join(list(logs.keys()))), RuntimeWarning
            )

        else:
            if self.completed_warmup_steps >= self.warmup_steps:

                if self.in_cooldown():
                    self.cooldown_counter -= 1
                    self.wait = 0

                if self.monitor_op(current, self.best):
                    self.best = current
                    self.wait = 0
                elif not self.in_cooldown():
                    self.wait += 1
                    if self.wait >= self.patience:
                        old_lr = float(K.get_value(self.model.optimizer.lr))
                        if old_lr > self.min_lr:
                            new_lr = old_lr * self.factor
                            new_lr = max(new_lr, self.min_lr)
                            K.set_value(self.model.optimizer.lr, new_lr)
                            if self.verbose > 0:
                                print('\nEpoch %05d: ReduceLROnPlateau reducing '
                                      'learning rate to %s.' % (epoch + 1, new_lr))
                            self.cooldown_counter = self.cooldown
                            self.wait = 0

    def on_batch_end(self, batch, logs=None):
        if self.completed_warmup_steps < self.warmup_steps:
            self.completed_warmup_steps += 1

            K.set_value(
                self.model.optimizer.lr, 
                self.initial_lr + ((self.base_lr - self.initial_lr) * (self.completed_warmup_steps / self.warmup_steps))
            )



