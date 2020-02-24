# Datasets preparation

Aim: balance pro and cons edges in datasets


## Datasets repartition

We take the same amount of pro and cons edges in each debate, so we drop a few edges to reach this objective.

We propose to split the corpus in:

| Dataset | Debates | Number of edges of each type | Proportion |
| --- | --- | --- | --- |
| train | 0..9, 15, 17..19, 21..25 | 11237 | 77.49% |
| dev | 14, 16, 20 | 2066 | 11.57% |
| test | 10..13 | 1953 | 10.94% |

As explain in the next section, it is not possible to balance nodes (regarding to their ingoing edges).

## Data exploration

### Ingoing edge repartition (by node)

Balancable nodes (wrt their incoming edges types) are too much rare.

	MATCH
	  (x: Sentence {origin: "kl"})
	RETURN
	  count(x) as total_number_of_nodes
	;
	// total_number_of_nodes
	// 34381
	
	MATCH
	  p=(:Sentence {origin: "kl"})<-[:Pro|:Cons]-()
	RETURN
	  count(p) as total_number_of_unique_edges
	;
	// total_number_of_unique_edges
	// 37302
	
	MATCH
	  p=(:Debate {origin: "kl"})-[:Contains]->()<-[:Pro|:Cons]-()
	RETURN
	  count(p) as total_number_of_edges_in_debate
	;
	// total_number_of_edges_in_debate
	// 42243

	MATCH
	  p=(d1:Debate {origin: "kl"})-[:Contains]->()<-[:Contains]-(d2: Debate {origin: "kl"})
	WHERE
	  d1.n < d2.n
	RETURN
	  count(p) as number_of_nodes_in_multiple_debates
	;
	// number_of_nodes_in_multiple_debates
	// 5733
	
	MATCH
	  p=(d1:Debate {origin: "kl"})-[:Contains]->()<-[:Contains]-(d2: Debate {origin: "kl"})
	WHERE
	  d1.n < d2.n
	RETURN
	  distinct ([d1.n, d2.n]) as debates_that_share_nodes
	;
	// debates_that_share_nodes
	// [0, 5]
	// [4, 5]
	// [4, 6]
	// [5, 6]
	
	MATCH
	  (x: Sentence {origin: "kl"})
	WHERE
	  not (x)<-[:Pro]-() or not (x)<-[:Cons]-()
	RETURN
	  count(x) as number_of_nodes_without_a_type_of_outgoing_edge
	;
	// number_of_nodes_without_a_type_of_outgoing_edge
	// 29752
		
	MATCH
	  (x: Sentence {origin: "kl"})
	WHERE
	  ()-[:Pro]->(x)<-[:Cons]-()
	RETURN
	  count(x) as number_of_nodes_with_both_types_of_ingoing_edge
	;
	// number_of_nodes_with_both_types_of_ingoing_edge
	// 4629


As we just see, if we want to balance dataset according to the type of ingoing edges for each nodes, we will have to throw away 29752 nodes, that is about 90% of our corpus.

Thus we will not balance datasets according to the type of the ingoing edges for each node.

### Edge repartition (by debate)

	MATCH
	  (d: Debate {origin: "kl"})
	WITH
	  d
	OPTIONAL MATCH
	  p_pro=(d)-[:Contains]->()<-[:Pro]-()
	WITH
	  d,
	  count(p_pro) as n_pro
	OPTIONAL MATCH
	  p_cons=(d)-[:Contains]->()<-[:Cons]-()
	WITH
	  d.n as debate_num,
	  n_pro,
	  count(p_cons) as n_cons
	WITH
	  debate_num,
	  n_pro,
	  n_cons,
	  CASE WHEN n_pro < n_cons THEN n_pro ELSE n_cons END as min_edges,
	  CASE WHEN n_pro > n_cons THEN n_pro ELSE n_cons END as max_edges
	RETURN
	  debate_num as debate_number,
	  n_pro as number_of_pro_edges,
	  n_cons as number_of_cons_edges,
	  min_edges as kept_edges,
	  max_edges - min_edges as dropped_edges
	;

| debate_number | number_of_pro_edges | number_of_cons_edges | kept_edges | dropped_edges |
| --- | --- | --- | --- | --- |
| 0 | 2390 | 2520 | 2390 | 130 |
| 1 | 91 | 93 | 91 | 2 |
| 2 | 197 | 66 | 66 | 131 |
| 3 | 210 | 79 | 79 | 131 |
| 4 | 522 | 724 | 522 | 202 |
| 5 | 7904 | 11429 | 7904 | 3525 |
| 6 | 661 | 963 | 661 | 302 |
| 7 | 171 | 108 | 108 | 63 |
| 8 | 433 | 358 | 358 | 75 |
| 9 | 59 | 45 | 45 | 14 |
| 10 | 399 | 439 | 399 | 40 |
| 11 | 627 | 784 | 627 | 157 |
| 12 | 452 | 575 | 452 | 123 |
| 13 | 482 | 475 | 475 | 7 |
| 14 | 355 | 360 | 355 | 5 |
| 15 | 210 | 95 | 95 | 115 |
| 16 | 203 | 353 | 203 | 150 |
| 17 | 183 | 170 | 170 | 13 |
| 18 | 227 | 116 | 116 | 111 |
| 19 | 135 | 157 | 135 | 22 |
| 20 | 1508 | 2259 | 1508 | 751 |
| 21 | 162 | 257 | 162 | 95 |
| 22 | 419 | 500 | 419 | 81 |
| 23 | 252 | 344 | 252 | 92 |
| 24 | 21 | 42 | 21 | 21 |
| 25 | 419 | 240 | 240 | 179 |
| --- | --- | --- | --- | --- |
| Total | 18692 | 23551 | 17853 | 6537 |

It appears to be feasible to balance datasets regarding to the edge repartition in debates.

Since debates 0, 4, 5 and 6 share nodes, they all have to be in the same dataset.

