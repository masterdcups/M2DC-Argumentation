# ML

## Modules

### Datasets

The *datasets* module contains:

	def create_dataset(dataset_name, n4j_graph, balanced=True):
	    """Create a dataset generator that yields ((text1,text2),weight) tuples.
	    
	    name: in {train, dev, dev1, dev2, test, test1, test2}
	    n4j_graph: connected neo4j graph
	    balanced: Return the same amout of rows for each class (=edge weight)
		"""
	    ...

All dataset generators yield *((s1,s2),w)* tuples where *s1* and *s2* are Kialo sentences (english language) and *w* is the weight of the edge from *s1* to *s2* (1 means pro, -1 means cons).  
With the ML naming convention, *x:=(s1,s2)* is the data row and *y:=w* is the corresponding label.

Available datasets are :

- **train**: 80% of kialo, but debates #14 and #16
- **dev**: union of *dev1* and *dev2* datasets
- **dev1**: 10% of kialo
- **dev2**: debate #16 (1.32% of kialo)
- **test**: union of *test1* and *test2* datasets
- **test1**: 10% of kialo
- **test2**: debate #14 (1.69% of kialo)

If the script is directly called, it uses the *utils* module to dump each dataset generator on disk. Use *-h* option for usage.

Balanced datasets are already generated and available in the  *datasets/* directory. You may want to *utils.load* them.



### Label count

The *main_count_labels.py* script counts label frequencies in datasets. It is mainly intended for debugging tasks, and may change or be removed in the future.

You may want to run:

	python3 main_count_labels.py datasets/*

to check that classes are balanced in each dataset

|dataset|n_rows|n_-1|n_1|
| --- | --- | --- | --- |
|dev1|3638|1819|1819|
|dev2|406|203|203|
|dev|3676|1838|1838|
|test1|3686|1843|1843|
|test2|710|355|355|
|test|3752|1876|1876|
|train|25292|12646|12646|



### Utils

The *utils* module contains:

	def dump(generator, filename):
	    """Dump a generator on disk"""
	    ...

	def load(filename):
	    """Load a generator from disk"""
	    ...

If the script is directly called, it produces a sample run.

