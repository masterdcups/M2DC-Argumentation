// Add 'depth' property
CREATE INDEX ON
  :Argument(depth)
;
MATCH
  (x)
SET
  x.depth = 100
;
MATCH
  (x)
WHERE
  not (x)-->()
SET
  x.depth = 0
;
CALL
  apoc.periodic.commit(
    "MATCH (x)-->(y) WHERE x.depth > y.depth + 1 SET x.depth = y.depth + 1 RETURN count(*) LIMIT 1",
    {limit:100}
  )
;

// Add 'debates' property
CREATE INDEX ON
  :Argument(debates);
MATCH
  (x)
SET
  x.debates = []
;
MATCH
  (x)
WHERE
  x.depth = 0
SET
  x.debates = [id(x)]
;
CALL
  apoc.periodic.commit(
    "MATCH (x)-->(y) WITH x, y UNWIND y.debates as idd WITH x, idd ORDER BY idd WITH x, collect(distinct(idd)) as debates WHERE x.debates <> debates SET x.debates = debates RETURN count(*) LIMIT 1",
    {limit: 100}
  )
;

// Count nodes and edges (by website)
MATCH 
  (x)
WITH
  x,
  size((x)-->()) as outdeg,
  size((x)<--()) as indeg
RETURN
  x.origin as origin,
  count(x) as n_nodes,
  sum(outdeg) as n_edges,
  max(outdeg),
  max(indeg),
  avg(x.depth),
  max(x.depth),
  count(distinct (x.description)) - 1 as n_descriptions,
  avg(size(x.description)),
  avg(size(x.label)),
  max(size(x.label)),
  stdev(size(x.label))
ORDER BY
  origin
;

// Count nodes and edges (by debate)
MATCH 
  (x)
WITH
  x,
  size((x)-->()) as outdeg,
  size((x)<--()) as indeg
UNWIND
  x.debates as idd
WITH
  x, 
  idd,
  outdeg,
  indeg
MATCH
  (d)
WHERE
  id(d) = idd
RETURN
  d.origin as origin,
  idd as debate_id,
  d.label as debate_label,
  count(x) as n_nodes,
  sum(outdeg) as n_edges,
  max(outdeg),
  max(indeg),
  avg(x.depth),
  max(x.depth),
  count(distinct (x.description)) - 1 as n_descriptions,
  avg(size(x.description)),
  avg(size(x.label)),
  max(size(x.label)),
  stdev(size(x.label))
ORDER BY
  origin, debate_id
;

// Cycles
MATCH
  (x)-[*..5]->(x)
RETURN
  x
;

// Arguments that are in multiple debates
MATCH
  (x)
WHERE
  size(x.debates) > 
