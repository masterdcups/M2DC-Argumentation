// Template for neo4j insertions
// Replace 'xxx' with the appropriate key ('wd', 'am-fr', etc.)


// Create indexes

CREATE INDEX ON 
    :Argument(n);

CREATE INDEX ON 
    :Argument(origin);



// Create nodes

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, n: toInteger(row.n), origin: "xxx"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"xxx"}),
	(n2:Argument {n: toInteger(row.n2), origin:"xxx"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///xxx_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"xxx"}),
    (n2:Argument {n: toInteger(row.n2), origin:"xxx"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);
