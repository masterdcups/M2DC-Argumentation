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

	python3 main_count_labels.py datasets/train.pkl datasets/dev.pkl datasets/dev1.pkl datasets/dev2.pkl datasets/test.pkl datasets/test1.pkl datasets/test2.pkl 

to check that classes are balanced in each dataset

|dataset|n_rows|n_-1|n_1|
| --- | --- | --- | --- |
|train|25292|12646|12646|
|dev1|3638|1819|1819|
|dev2|406|203|203|
|dev|3676|1838|1838|
|test1|3686|1843|1843|
|test2|710|355|355|
|test|3752|1876|1876|


## Modules

### Datasets

The *datasets* module contains:

	def sentence_generator(n4j_graph):
    	"""Create a generator for all sentences (nodes)"""
	    ...
	    
	def argument_generator(dataset_name, n4j_graph, balanced=False):
	    """Create a dataset generator that yields ({'n1':_, 'n2':_},{'class':_}) tuples.
	    name: in {train, dev, dev1, dev2, test, test1, test2}
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

- **train**: 80% of kialo, but debates #14 and #16
- **dev**: union of *dev1* and *dev2* datasets
- **dev1**: 10% of kialo
- **dev2**: debate #16 (1.32% of kialo)
- **test**: union of *test1* and *test2* datasets
- **test1**: 10% of kialo
- **test2**: debate #14 (1.69% of kialo)

If the script is directly called, it uses the *utils* module to dump each dataset generator on disk. Use *-h* option for usage.

The sentence generator and all balanced dataset generators are already generated and available in the  *datasets/* directory. You may want to *utils.load* them.





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

If the script is directly called, it produces a sample run.

