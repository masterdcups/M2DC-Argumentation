# ML

## Scripts

### Main script

For now, the *main.py* script is a sample run:

1. Create and dump the sentence generator on disk (if missing)
2. Create and dump the given argument generator on disk (if missing). By default it uses the 'dev2' dataset.
3. Load dumped generators
4. Apply an arbitrary transformation on sentences (upper case)
5. Map arguments with the processes sentences
6. Print rows


### Label count

The *main_count_labels.py* script counts label frequencies in datasets. It is mainly intended for debugging tasks, and may change or be removed in the future.

You may want to run:

	d='../../../data/raw'
	python3 main_count_labels.py $d/train.pkl $d/dev.pkl $d/test.pkl

to check that classes are balanced in each dataset

|dataset|n_rows|n_-1|n_1|
| --- | --- | --- | --- |
|train|22973|11237|11237|
|dev|4132|2066|2066|
|test|3906|1953|1953|


## Modules

### Datasets

The *datasets* module contains:

	def sentence_generator(n4j_graph):
    	"""Create a generator for all sentences (nodes)"""
	    ...
	    
	def argument_generator(dataset_name, n4j_graph, balanced=False):
	    """Create a dataset generator that yields ({'n1':_, 'n2':_},{'class':_}) tuples.
	    name: in {train, dev, test}
	    n4j_graph: connected neo4j graph
	    balanced: Return the same amout of rows for each class (edge weight)
	    """
	    ...

	def sentence_mapper(sentence_gen):
	    """Mapper: map sentences on 'n=n1' and 'n=n2' condition"""
	    ...

	def map_sentences(argument_gen, sentence_gen):
	    """Map sentences to arguments (use the 'sentence_mapper')"""
	    ...
	    

The sentence generator yields {'text': _, 'n': _} dicts.  
Argument generators yield ({'n1':_, 'n2':_}, {'class':_}) tuples of dicts.  
The sentence mapping consist to map arguments with the (preprocessed) sentences. Note that all sentences have to be read before mapping, so it breaks the pipeline.

All sentences are taken from Kialo (thus in english), classes are 1.0 (pro-edges) and -1.0 (cons-edges).

Available datasets are :

- **train**: debates 0..9, 15, 17..19, 21..25
- **dev**: debates 14, 16, 20
- **test**: debates 10..13

If the script is directly called, it uses the *utils* module to dump each dataset generator on disk. Use *-h* option for usage.

The sentence generator and all balanced dataset generators are already generated and available in the  *../../../data/raw/* directory. You may want to *utils.load* them.





### Utils

The *utils* module contains:

	def dump(generator, filename):
	    """Dump a generator on disk"""
	    ...

	def load(filename):
	    """Load a generator from disk"""
	    ...

	def gmap(generator, f):
	    """Map the function 'f' to every item of the generator"""
		...

	def merge_dicts(generator):
	    """Merge yielded items: some dicts with distinct keys -> a dict with all keys"""
		...
	
	def split_dicts(generator, *key_lists):
	    """Split yielded items in dicts corresponding to the given key lists"""
		...

	def to_csv(generator, filename=None):
	    """CSV of a generator that yields dicts"""
	    ...

	def from_csv(filename):
	    """Read a csv and return a generator that yield dicts correspnding to columns"""
		...



If the script is directly called, it produces a sample run.

