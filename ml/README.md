# Machine Learning for argument pro/con classification

This directory contains code to preprocess arguments (which are pairs of text labeled with the type of relation (pro & con)) using NLP techniques, train machine learning models on arguments and evaluate the quality of said models.

## User guide

### Python environment setup
```
	conda env create -f setup/environment.yml
	conda activate argumentation_ml

	# This should download necessary corpora/models.
	# It does not because I don't remember which one were downloaded.
	# You should get some error message telling you to somehow download
	# a thing. Please update nlp_setup.py to reflect what you did.
	python setup/nlp_setup.py
```

### Usage

All input and output data paths should be declared in the `Makefile`. Make sure everything is setup correcly before running.

`DATA_DIR=data` by default, with raw data found in `DATA_DIR/raw` and outputs in `OUTPUT_DIR=DATA_DIR/basic`.

```
	cd ml/
	conda activate argumentation_ml
	make
```


This will generate the following files:

 - Preprocessing (in `OUTPUT_DIR/preprocessed/`):

   - `dictionary.pkl`
   - `tfidf.pkl`
   - `preprocessed_nodes.pkl`
   - `(training, validation, test)preprocessed_arguments.pkl`

 - Training (in `OUTPUT_DIR/models/`):

   - `model.pkl`

 - Evaluation (in `OUTPUT_DIR/evaluation/`):

   - nothing yet (script outputs metrics to stdout)

There is (at least one) file dedicated to each output, which can be found in `src/`. 
Calling the scripts without arguments will display their individual user guide (argparse).

## Developper guide

### General architecture
`Makefile` defines the paths of every input and output of each scripts.

`src/` contains the main scripts. They take paths / filenames as input and output files to disk. These scripts should be as minimal as possible (parse arguments, load files, pass data to library functions, save files).

`cfg/` contains yaml configuration files for the main scripts.

`mllib/` is where the real work is done. This is a module, with the following structure:

 - `preprocessing`:

   - `dataset_preparation` (dataset generation, loading, utilities)
   - `text_preprocessing` (preprocessing of individual text documents)
   - `argument_preprocessing` (processing of arguments)
   - `ml_preprocessing` ((X,y) generators, adaptors, ml utilities)

 - `models` (training procedures and models)
 - `evaluation` (computing metrics, maybe uploading results)

Module functions should be pure: no side-effects apart from printing to stdout (or loading files through generator getters passed as parameters).

Module scripts cannot be called as main normally. To run `text_preprocessing.py` as a main file (for debugging purpose), execute:
```
	python3 -m mllib.preprocessing.text_preprocessing.text_preprocessing args
```
Please create a test method (or at least a human-readable print loop) whenever you use these mains (don't throw away the debugging code, clean it up and save it).
(the current mains might very well be unusable/obsolete code)

### Input / output
Depending on the context, module functions take as inputs single files (dictionary, models, DataFrame) or functions returning a generator. They return a single file or a generator.

Examples of functions returning a generator:
```
	generator_getter = lambda: range(10)
	generator_getter = lambda: utils.load('file.pkl')

	generator = generator_getter()
```
File loading/dumping is mostly done with pkl, either directly or through `mllib.preprocessing.dataset_preparation.utils`.

### Preprocessing
The pipeline currently involves:

 - Preprocessing the node documents using corpus agnostic techniques, to precompute nlp features
 - Fitting of gensim's Dictionary and TfidfModel on the node documents appearing in the training arguments
 - Extraction of argument nodes Tf-Idf vectors and their cosine similarities
 - Generation of pandas.DataFrame dumps containing the preprocessed arguments

It should be noted that the dumped DataFrame contains Tf-Idf vectors in a sparse format, which cannot be use directly by machine learning methods.

### Training
The pipeline currently involves:

 - Defining a model (currently sklearn.linear_model.LogisticRegression())
 - Defining a mapping between the preprocessed argument DataFrame columns and the inputs/outputs of the model (`ml_adaptors.py`)
 - Defining a training procedure (with a generator (`ml_generators.py`))
 - Dumping the model to disk

### Evaluation
The pipeline currently involves:

 - Defining evaluation generators, using the previously defined mapping
 - Defining the metrics to evaluate
 - Loading the model (non-trivial for Deep Learning models)
 - Dumping the metrics evaluation for training and validation sets

### Makefile
The source code is excluded from the prerequisites (very likely to change).

### Git


`data/.gitignore`, keeps empty data dir in repo:
```
	*
	!raw/
	!.gitignore
```

`.gitignore`:
```
	*__pycache__/
```

