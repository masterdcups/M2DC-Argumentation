// Auto-generated insertion instructions.


// Create indexes

CREATE INDEX ON 
    :Sentence(n);

CREATE INDEX ON 
    :Sentence(origin);

CREATE INDEX ON 
    :Sentence(n,origin);



// Create 'Sentence' nodes

LOAD CSV WITH HEADERS FROM 
    "file:///am-tr_nodes.csv" AS row 
CREATE 
    (:Sentence {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-tr"});



// Create 'Pro' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-tr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Sentence {n: toInteger(row.n1), origin:"am-tr"}),
	(n2:Sentence {n: toInteger(row.n2), origin:"am-tr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Pro {w: toFloat(row.weight)}]->(n2);



// Create 'Cons' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-tr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Sentence {n: toInteger(row.n1), origin:"am-tr"}),
    (n2:Sentence {n: toInteger(row.n2), origin:"am-tr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Cons {w: toFloat(row.weight)}]->(n2);
