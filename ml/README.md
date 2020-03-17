# Machine Learning for argument pro/con classification

This directory contains code to preprocess arguments (which are pairs of text labeled with the type of relation (pro & con)) using NLP techniques, train machine learning models on arguments and evaluate the quality of said models.

## User guide

### Python environment setup
```
	conda env create -f setup/environment.yml
	conda activate argumentation_ml

	# This download necessary NLP corpora/models.
	python3 setup/setup_nlp.py
```

### Usage

All input and output data paths should be declared in the `Makefile`. Make sure everything is setup correcly before running.

Raw word embeddings and sentiment lexicons need to be downloaded separately, in text format (meaning not binary, but can be .txt or .vec), in the `data/word_embeddings` and `data/lexicons` directories :

 - word embeddings can be fasttext or GloVe (others should work, but were not tried) 
 - sentiment lexicon can be [IBM's UniGram lexicon](https://www.research.ibm.com/haifa/dept/vst/debating_data.shtml) (recommended, found in section 3.2 (sentiment composition lexicon)), [textblob's lexicon](https://github.com/sloria/TextBlob/blob/dev/textblob/en/en-sentiment.xml) (others should work, but were not tried)


`DATA_DIR=data` by default, with raw data found in `DATA_DIR/raw` and outputs in `OUTPUT_DIR=DATA_DIR/basic`.

```
	cd ml/
	conda activate argumentation_ml
	make
```

This will preprocess raw data, train a model on it and print to stdout evaluation metrics. Processed files can be found in `OUTPUT_DIR/`.


## Developper guide

`Makefile` defines the paths of every input and output of each scripts, and calls `src/` scripts to generate the target files.

`src/` contains the main scripts. They take paths / filenames as input and output files to disk. 

Description of `src/*.py` scripts:

 - `preprocess_nodes.py` along with `src/TextPreprocessor.py` preprocesses raw sentences (`DATA_DIR/raw/sentences.pkl`): tokenization, PoS tagging and lemmatization
 - `preprocess_arguments.py` along with `mllib/preprocessing/argument_preprocessing/argument_preprocessing.py` preprocesses arguments (pairs of documents): joins the argument nodes (based on the edges), and does any work specific to arguments (e.g.: difference of document lengths)
 - `preprocess_[vec_embedding|sentiment_lexicon].py` preprocess the word embeddings and sentiment lexicons. These scripts might need to be modified if other data is used.
 - `model/EncDec/train_EncDec_model.py` along with `model/EncDec/EncDec.py` trains an Encoder-Decoder based model. 
 - `inference.py` loads a trained model (along with embeddings/lexicons) and outputs predictions for arguments (which are currently defined in the script).

The Makefile (should) do everything once paths are set and data downloaded, and can therefore be used as a kind of code map. The scripts' mains use the argparse library to parse arguments, and print some help regarding the scripts arguments.
