
// Auto-generated instructions


// Create indexes

CREATE INDEX ON 
    :Argument(n);

CREATE INDEX ON 
    :Argument(origin);

CREATE INDEX ON 
    :Argument(n,origin);



// Create nodes

LOAD CSV WITH HEADERS FROM 
    "file:///kl_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "kl"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///kl_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"kl"}),
	(n2:Argument {n: toInteger(row.n2), origin:"kl"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///kl_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"kl"}),
    (n2:Argument {n: toInteger(row.n2), origin:"kl"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);
