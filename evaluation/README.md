# Evaluation

evaluation.py defines an `evaluate` method which takes a nx.DiGraph object whose `weight` node and edge properties respectively correspond to intrinsic strength, and polarity and strength of the relation (interval -1 to 1). `evaluate` returns a dictionary mapping argument (node) names to their overall evaluated strength.

Sample run:
```
	python3 evaluation.py
```

produces (an evaluation of the semantic defining paper's example graph):
```
	Argument            Strength            
	j                   0.99                
	i                   0.22                
	h                   0.99                
	f                   0.27                
	g                   0.00                
	e                   0.40                
	c                   0.54                
	d                   0.22                
	b                   0.54                
	a                   0.60                
```
