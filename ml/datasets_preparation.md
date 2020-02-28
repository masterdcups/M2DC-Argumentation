# Datasets preparation

Aim: balance pro and cons edges in datasets


## Datasets repartition

We take the same amount of pro and cons edges in each debate, so we drop a few edges to reach this objective.

We propose to split the corpus in:

| Dataset | Debates | Number of edges | Proportion |
| --- | --- | --- | --- |
| train | 0..9, 15, 17..19, 21..25 | 22973 | 74.08% |
| dev | 14, 16, 20 | 4132 | 13.32% |
| test | 10..13 | 3906 | 12.59% |

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
	  (:Sentence {origin: "kl"})<-[r:Pro|:Cons]-()
	RETURN
	  count(distinct r) as total_number_of_edges
	;
	// total_number_of_edges
	// 37302

	MATCH
	  (d1:Debate {origin: "kl"})-[:Contains]->(x:Sentence)<-[:Contains]-(d2: Debate {origin: "kl"})
	WHERE
	  d1.n < d2.n
	RETURN
	  count(distinct x) as number_of_nodes_in_multiple_debates
	;
	// number_of_nodes_in_multiple_debates
	// 3453
	
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
	  count(distinct x) as number_of_nodes_without_a_type_of_ingoing_edge
	;
	// number_of_nodes_without_a_type_of_ingoing_edge
	// 29752
		
	MATCH
	  (x: Sentence {origin: "kl"})
	WHERE
	  ()-[:Pro]->(x)<-[:Cons]-()
	RETURN
	  count(distinct x) as number_of_nodes_with_both_types_of_ingoing_edge
	;
	// number_of_nodes_with_both_types_of_ingoing_edge
	// 4629
	
	MATCH 
	  (x:Sentence {origin: "kl"}) 
	WITH
	  x
	OPTIONAL MATCH
	  (x)<-[p:Pro]-() 
	WITH
	  x,
	  count(p) as n_pro 
	OPTIONAL MATCH
	  (x)<-[c:Cons]-() 
	WITH
	  x,
	  n_pro, 
	  count(c) as n_cons 
	WITH
	  x, 
	  n_pro, 
	  n_cons, 
	  CASE 
	    WHEN n_pro > n_cons THEN n_cons 
	    ELSE n_pro 
	  END as n_min 
	RETURN 
	  sum(n_min) * 2 as n_kept_edges
	;
	// n_kept_edges
	// 15358


As we just see, if we want to balance dataset according to the type of ingoing edges for each nodes, we will keep 15358 edges, that is, we will drop 21944 edges.

Thus we will not balance datasets according to the type of the ingoing edges for each node.

### Edge repartition (by debate)

	MATCH
	  (d: Debate {origin: "kl"})
	WITH
	  d
	OPTIONAL MATCH
	  (d)-[:Contains]->()<-[p:Pro]-()
	WITH
	  d,
	  count(distinct p) as n_pro
	OPTIONAL MATCH
	  (d)-[:Contains]->()<-[c:Cons]-()
	WITH
	  d,
	  n_pro,
	  count(distinct c) as n_cons
	WITH
	  d.n as debate_num,
	  n_pro,
	  n_cons,
	  CASE WHEN n_pro < n_cons THEN n_pro ELSE n_cons END as min_edges,
	  CASE WHEN n_pro > n_cons THEN n_pro ELSE n_cons END as max_edges
	RETURN
	  debate_num as debate_number,
	  n_pro as n_pro_edges,
	  n_cons as n_cons_edges,
	  min_edges as n_kept_edges,
	  max_edges - min_edges as n_dropped_edges
	;
| debate_number | n_pro_edges | n_cons_edges | n_kept_edges | n_dropped_edges |
| --- | --- | --- | --- | --- |
| 0 | 2390 | 2520 | 4780 | 130 |
| 1 | 91 | 93 | 182 | 2 |
| 2 | 197 | 66 | 132 | 131 |
| 3 | 210 | 79 | 158 | 131 |
| 4 | 522 | 724 | 1044 | 202 |
| 5 | 7904 | 11429 | 15808 | 3525 |
| 6 | 661 | 963 | 1322 | 302 |
| 7 | 171 | 108 | 216 | 63 |
| 8 | 433 | 358 | 716 | 75 |
| 9 | 59 | 45 | 90 | 14 |
| 10 | 399 | 439 | 798 | 40 |
| 11 | 627 | 784 | 1254 | 157 |
| 12 | 452 | 575 | 904 | 123 |
| 13 | 482 | 475 | 950 | 7 |
| 14 | 355 | 360 | 710 | 5 |
| 15 | 210 | 95 | 190 | 115 |
| 16 | 203 | 353 | 406 | 150 |
| 17 | 183 | 170 | 340 | 13 |
| 18 | 227 | 116 | 232 | 111 |
| 19 | 135 | 157 | 270 | 22 |
| 20 | 1508 | 2259 | 3016 | 751 |
| 21 | 162 | 257 | 324 | 95 |
| 22 | 419 | 500 | 838 | 81 |
| 23 | 252 | 344 | 504 | 92 |
| 24 | 21 | 42 | 42 | 21 |
| 25 | 419 | 240 | 480 | 179 |
| --- | --- | --- | --- | --- |
| Total | 18692 | 23551 | 35706 | 6537 |

*Note:* the total kept+dropped is slightly bigger than the number of edges since somes edges occurs in multiple debates: there are multiple counted here

It appears to be feasible to balance datasets regarding to the edge repartition in debates, as we drop only 6537 edges.

Since debates 0, 4, 5 and 6 share nodes, they all have to be in the same dataset.

