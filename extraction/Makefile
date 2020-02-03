include Makefile_settings.txt

# Website to extract (wd=wikidebats, am-xxx=arguman, kl=kialo)
ORIGINS = wd am-fr am-en am-es am-pl am-tr am-ch kl

# Location of cypher-shell executable
CYPHER_SHELL = $(N4J_DB_PATH)/bin/cypher-shell -a $(N4J_URI) -u $(N4J_USER) -p $(N4J_PASS) --format plain



all: .inserted
download:  $(foreach o, $(ORIGINS), $(N4J_DB_PATH)/import/$(o)_nodes.csv $(N4J_DB_PATH)/import/$(o)_edges.csv)

.inserted: all_insertion.cql $(foreach o, $(ORIGINS), $(N4J_DB_PATH)/import/$(o)_nodes.csv $(N4J_DB_PATH)/import/$(o)_edges.csv)
	$(CYPHER_SHELL) 'MATCH (x) OPTIONAL MATCH (x)-[r]->(y) DELETE x, y, r RETURN count(*) as deleted'
	$(CYPHER_SHELL) < $<
	$(CYPHER_SHELL) 'MATCH (x) RETURN count(x) as inserted'
	date > $@

$(N4J_DB_PATH)/import/%.csv: ./%.csv
	cp $< $(N4J_DB_PATH)/import

%_nodes.csv %_edges.csv:
	./extract.sh $(subst -, ,$*) --n_threads $(N_THREADS)


all_insertion.cql: $(foreach o, $(ORIGINS), $(o)_insertion.cql)
	cat $^ > $@

%_insertion.cql: insertion_template.cql
	tail -n +3 $< | sed s/xxx/$*/ > $@

clean:
	rm -f $(N4J_DB_PATH)/import/*.csv *.csv *_insertion.cql .inserted


.NOTPARALLEL: %_nodes.csv %_edges.csv .inserted
.PRECIOUS: %_nodes.csv %_edges.csv
.PHONY: all download clean
