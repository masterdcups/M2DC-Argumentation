
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
    "file:///am-ch_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-ch"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-ch_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-ch"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-ch"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-ch_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-ch"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-ch"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///am-en_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-en"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-en_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-en"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-en"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-en_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-en"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-en"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///am-es_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-es"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-es_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-es"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-es"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-es_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-es"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-es"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///am-fr_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-fr"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-fr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-fr"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-fr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-fr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-fr"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-fr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///am-pl_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-pl"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-pl_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-pl"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-pl"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-pl_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-pl"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-pl"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///am-tr_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "am-tr"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-tr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-tr"}),
	(n2:Argument {n: toInteger(row.n2), origin:"am-tr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///am-tr_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"am-tr"}),
    (n2:Argument {n: toInteger(row.n2), origin:"am-tr"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);

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
    "file:///wd_nodes.csv" AS row 
CREATE 
    (:Argument {url: row.url, label: row.label, description: row.description, n: toInteger(row.n), origin: "wd"});



// Create 'Support' edges

LOAD CSV WITH HEADERS FROM 
    "file:///wd_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) > 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"wd"}),
	(n2:Argument {n: toInteger(row.n2), origin:"wd"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Support {w: toFloat(row.weight)}]->(n2);



// Create 'Attack' edges

LOAD CSV WITH HEADERS FROM 
    "file:///wd_edges.csv" AS row
WITH 
    row
WHERE
    toFloat(row.weight) < 0
MATCH
    (n1:Argument {n: toInteger(row.n1), origin:"wd"}),
    (n2:Argument {n: toInteger(row.n2), origin:"wd"})
WITH
    row, n1, n2
CREATE
    (n1)-[:Attack {w: toFloat(row.weight)}]->(n2);
