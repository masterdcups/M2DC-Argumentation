from keras.layers import Input
from keras.layers import Embedding
from keras.layers import LSTM
from keras.layers import Bidirectional
from keras.layers import concatenate, add

from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras.optimizers import Adam

from keras.models import Model

import numpy as np

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
    default_options["n_classif"] = 3
    default_options["lrate"] = 0.001

    return default_options


def CocarascuModel(options=None):
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
   
    default_options = getOptionsCocarascu()
    if options is None:
        options = default_options
    else:
        default_options.update(options)
        options = default_options
    
    maxlen = default_options["maxlen"]
    embedded_size = default_options["embedded_size"] 
    max_features = default_options["vocab_size"] 
    embedding_matrix = default_options["embedding_matrix"]
    
    argA = Input(shape=(maxlen,))
    argB = Input(shape=(maxlen,))
    
    #Model for arg1
    x = Embedding(max_features,
                  embedded_size, 
                  weights=options["embedding_matrix"], 
                  trainable=options["train_embedding"])(argA)
    if options["lstm"] == "bi":
        x = Bidirectional(LSTM(default_options["n_lstm"], 
                           activation=options["acti_lstm"],
                           return_sequences=False))(x) 
    else:
        x = LSTM(default_options["n_lstm"], 
                 activation=options["acti_lstm"],
                 return_sequences=False)(x) 
        
    x = Dropout(rate=options["dropout_rate"])(x)
    x = Model(inputs=argA, outputs=x)
    
    #Model for arg2
    y = Embedding(max_features,
                  embedded_size, 
                  weights=options["embedding_matrix"], 
                  trainable=options["train_embedding"])(argB)
    if options["lstm"] == "bi":
        y = Bidirectional(LSTM(default_options["n_lstm"], 
                           activation=options["acti_lstm"],
                           return_sequences=False))(y) 
    else:
        y = LSTM(default_options["n_lstm"], 
                 activation=options["acti_lstm"],
                 return_sequences=False)(y) 
    y = Dropout(rate=options["dropout_rate"])(y)
    y = Model(inputs=argB, outputs=y)
    
    #Merge models
    if options["merge"]=="concat":
        combined = concatenate([x.output, y.output])
    elif options["merge"] == "sum":
        combined = add([x.output, y.output])
                
    z = Dense(options["n_nn"], activation="relu")(combined) 
    z = Dense(options["n_classif"], activation="softmax")(z)
    model = Model(inputs=[x.input, y.input], outputs=z)
    
    adam = Adam(lr=options["lrate"])
    model.compile(optimizer=adam, loss="categorical_crossentropy", metrics=["accuracy"])
    
    print(model.summary())
    return model
   

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

"""
Methods implemented by Carstents-Toni in
'Using argumentation to improve classification in Natural Language problems'
Method: SVM, Random Forest
"""

def svmModel():
    model = SVC(C=1, kernel='poly')
    return model

def rfModel():
    model = RandomForestClassifier(n_estimators=256)
    return model


#def main():
#
#    batch_size = 128
#    options = {}
#    options["n_classif"] = 2
#    model = CocarascuModel(options)
#    inputA = np.random.randint(1,high=50, size=(256,50))
#    inputB = np.random.randint(1,high=50, size=(256,50))
#    labels = np.random.randint(0,high=1, size=(256,2))
#    model.fit([inputA, inputB], labels, epochs=3, batch_size=batch_size)

#if __name__=="__main__":
#    main()
