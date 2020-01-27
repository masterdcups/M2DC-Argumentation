// Template for neo4j insertions
// Replace 'xxx' with the appropriate key ('wd', 'am-fr', etc.)


// Create indexes

CREATE INDEX ON 
    :Sentence(n);

CREATE INDEX ON 
    :Sentence(origin);

CREATE INDEX ON 
    :Sentence(n,origin);



// Create 'Sentence' nodes

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_nodes.csv" AS row 
CREATE 
    (:Sentence {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "xxx"});



// Create 'Pro' edges

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Sentence {n: toInteger(row.n1), origin:"xxx"}),
	(n2:Sentence {n: toInteger(row.n2), origin:"xxx"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Pro {w: toFloat(row.weight)}]->(n2);



// Create 'Cons' edges

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Sentence {n: toInteger(row.n1), origin:"xxx"}),
    (n2:Sentence {n: toInteger(row.n2), origin:"xxx"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Cons {w: toFloat(row.weight)}]->(n2);



// Create 'Argument' nodes

MATCH
  (x:Sentence)-[:Pro]->(y:Sentence)
CREATE
  (x)<-[:IsPremise]-(:Argument {label: id(x)+" -> "+id(y)})-[:IsConclusion]->(y)
;
MATCH
  (x:Sentence)-[:Cons]->(y:Sentence)
CREATE
  (x)<-[:IsPremise]-(:Argument {label: id(x)+ " -> ¬"+id(y)})-[:IsNotConclusion]->(y)
;


// Create 'Support' edges

MATCH
  (x:Argument)-[:IsConclusion]->()<-[:IsConclusion]-(y:Argument)
CREATE
  (x)-[:Support]->(y)
;
MATCH
  (x:Argument)-[:IsNotConclusion]->()<-[:IsNotConclusion]-(y:Argument)
CREATE
  (x)-[:Support]->(y)
;
MATCH
  (x:Argument)-[:IsConclusion]->()<-[:IsPremise]-(y:Argument)
CREATE
  (x)-[:Support]->(y)
;


// Create 'Attack' edges

MATCH
  (x:Argument)-[:IsConclusion]->()<-[:IsNotConclusion]-(y:Argument)
CREATE
  (x)-[:Attack]->(y)
;
MATCH
  (x:Argument)-[:IsNotConclusion]->()<-[:IsConclusion]-(y:Argument)
CREATE
  (x)-[:Attack]->(y)
;
MATCH
  (x:Argument)-[:IsNotConclusion]->()<-[:IsPremise]-(y:Argument)
CREATE
  (x)-[:Attack]->(y)
;

