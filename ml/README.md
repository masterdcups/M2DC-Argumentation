# Machine Learning for argument pro/con classification

This directory contains code to preprocess arguments (which are pairs of text labeled with the type of relation (pro & con)) using NLP techniques, train machine learning models on arguments and evaluate the quality of said models.

## User guide

### Python environment setup
```
	conda env create -f setup/environment.yml
	conda activate argumentation_ml

	# This download necessary corpora/models.
	python3 setup/setup_nlp.py
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

There is (at least one) script dedicated to each output, which can be found in `src/`. 
Calling the scripts without arguments will display their individual user guide (argparse).

## Developper guide

### General architecture
`Makefile` defines the paths of every input and output of each scripts, and calls `src/` scripts to generate the target files.

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

Module scripts cannot be called as main in the usual fashion. To run `text_preprocessing.py` as a main file (for debugging purpose ONLY, and even then..), execute:
```
	python3 -m mllib.preprocessing.text_preprocessing.text_preprocessing foo
```
Please create a test method (or at least a human-readable print loop) whenever you use these mains (don't throw away the debugging code, clean it up and save it).
(the current mains are mostly development/garbage code)

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
 - Defining a mapping between the preprocessed argument DataFrame columns and the inputs/outputs of the model
 - Defining a training procedure
 - Dumping the model to disk

### Evaluation
The pipeline currently involves:

 - Defining evaluation generators, using the previously defined mapping
 - Defining the metrics to evaluate
 - Loading the model (non-trivial for Deep Learning models)
 - Dumping the metrics evaluation for training and validation sets

### Modifying the pipelines

If a script requires parameters (like `src/train_dictionary.py` with the vocabulary size), they must be passed through configuration files (`cfg/dictionary.yaml`).

#### Features
Features can be split in three categories:

 - corpus agnostic text feature: does not need to be trained on anything. Lemmatization (using pretrained model), length of sentences and such fit here.
 - corpus dependent text feature: needs to be trained. Tf-Idf, Dictionary of most frequent words, and word embeddings fit here.
 - argument feature: needs to be computed on two nodes. The cosine similarity of Tf-Idf vectors is an example.

Generation of preprocessed arguments is therefore done in three phases, and defined in two different files two files. Each file output (new trained model, type of preprocessed file) requires a new Makefile rule and a new `src/` script.

`text_preprocessing.py` contains code relative to NLP: how to lemmatize, how to fit the tf-idf model, how to compute the length of a sentence. It also contains `preprocessed_node_generator()` which applies the corpus agnostic transformations.

`argument_preprocessing.py` contains code relative to arguments and their nodes corpus dependent features: how apply the tf-idf model (no knowledge of NLP required) on single documents, how to compute the tf-idf cosine similarity between an argument nodes. All of this is done in `preprocessed_argument_df()`.

#### Models
##### Defining data mappings
Feeding data to ML models requires a bit of boiler-plate code, mostly when matching model inputs to data. `ml_preprocessing` contains:

 - `ml_adaptors.py`: mappings between data and dictionary of numpy arrays
 - `ml_generators.py`: application of a mapping to batches of samples extracted from the data

The current adaptor and generator both work on pandas.DataFrame objects, which they help converting to dictionary of numpy arrays (keys being 'X' and 'y').

To define a new feature in a mapping, add to its ('X' or 'y') 'columns' dictionary another dictionary.
```
'X': {
	'columns': {
		'DataFrame_column1_name': {},
		'DataFrame_column2_name': {
			'function': func,
			'name': 'new_column2_name'
		}
	},
	'parameters': {'merge': True}
}
```
This example will result in the 'X' key containing a dictionary with keys `DataFrame_column1_name` and `new_column2_name` with values being the application of the defined function (a default one expanding scalar columns to 2D np.array is used when undefined). 'merge' is set to True, meaning all columns values (for 'X') will be concatenated to return a np.array instead of a dict.
This works the same way for 'y'.

The mapping function should take a DataFrame column (`df[column_name]`) as input and return a np.array of shape `(column_length, x)` (x=1 for scalars, size of vocabulary for sparse tf-idf to dense tf-idf, etc)

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

