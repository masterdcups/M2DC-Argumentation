"""
Module: datasets

Generate kialo datasets from the neo4j database.
 - as a module: *create_dataset* returns a dataset generator
 - as a script: the script outputs all dataset generators using utils.dump

"""
import py2neo




def sentence_generator(n4j_graph):
    """Create a generator for all sentences (nodes)"""
    
    query = """
    MATCH
        (x: Sentence {origin: "kl"})<-[:Contains]-(deb:Debate)
    WITH
        x.label as label,
        x.n as n,
        deb.n as debn,
        rand() as rdm
    MATCH
        (y: Sentence {origin: "kl"})
    WHERE
        y.n = debn
    RETURN
        label,
        n,
        y.label as debate
    ORDER BY
        rdm
    """
    for record in n4j_graph.run(query):
        yield {
            's': record['label'],
            'n': record['n'],
            'debate_name': record['debate'],
            }



def argument_generator(dataset_name, n4j_graph, balanced=False):
    """Create a dataset generator that yields ({'n1':_, 'n2':_},{'class':_}) tuples.
    name: in {train, dev, dev1, dev2, test, test1, test2}
    n4j_graph: connected neo4j graph
    balanced: Return the same amout of rows for each class (edge weight)

    Available datasets:
        train: 80% of kialo dataset but debates #14 and #16
        dev1: 10% of kialo dataset but debates #14 and #16
        dev2: kialo debate #16 (1.32% of kialo)
        dev: union of dev1 and dev2
        test1: 10% of kialo dataset but debates #14 and #16
        test2: kialo debate #14 (1.69% of kialo)
        test: union of test1 and test2
    """

    if balanced:
        query = _balanced_dataset_query(dataset_name, n4j_graph)
    else:
        query = _unbalanced_dataset_query(dataset_name)

    for record in n4j_graph.run(query):
        yield ({'n1': record['x'], 'n2': record['y']}, {'class': record['w']})




def sentence_mapper(sentence_gen):
    """Mapper: map sentences on 'n=n1' and 'n=n2' condition"""

    # Collect ALL the sentences before yielding anything :-(
    sentences = {}
    for s in sentence_gen:
        sentences[s['n']] = s

    def _mapper(row):
        X, y = row
        X2 = {}
        for k,v in sentences[X['n1']].items():
            X2[k+'1'] = v
        for k,v in sentences[X['n2']].items():
            X2[k+'2'] = v
        return (X2, y)

    return _mapper 

def map_sentences(argument_gen, sentence_gen):
    """Map sentences to arguments (use the 'sentence_mapper')"""
    return utils.gmap(argument_gen, sentence_mapper(sentence_gen))


def _traintestdev_condition(dataset_name):
    """Neo4j condition (cypher sub-query) corresponding to a dataset name

    Available datasets:
        train: 80% of kialo dataset but debates #14 and #16
        dev1: 10% of kialo dataset but debates #14 and #16
        dev2: kialo debate #16 (1.32% of kialo)
        dev: union of dev1 and dev2
        test1: 10% of kialo dataset but debates #14 and #16
        test2: kialo debate #14 (1.69% of kialo)
        test: union of test1 and test2
    """
    if dataset_name == "train":
        condition = "x.n % 10 > 2 and not debate.n = 14 and not debate.n = 16"
    elif dataset_name == "dev":
        condition = "x.n % 10 = 0 and not debate.n = 14"
    elif dataset_name == "dev1":
        condition = "x.n % 10 = 0 and not debate.n = 14 and not debate.n = 16"
    elif dataset_name == "dev2":
        condition = "debate.n = 16"
    elif dataset_name == "test":
        condition = "x.n % 10 = 1 and not debate.n = 16"
    elif dataset_name == "test1":
        condition = "x.n % 10 = 1 and not debate.n = 14 and not debate.n = 16"
    elif dataset_name == "test2":
        condition = "debate.n = 14"
    else:
        raise ValueError("Dataset name must be in {train, dev, dev1, dev2, test, test1, test2}")
    return condition




def _balanced_dataset_query(dataset_name, n4j_graph):
    """Cypher query for a given dataset (balanced classes)
    Return sentence numbers (sentence.n) for kialo
    """

    condition = _traintestdev_condition(dataset_name)
    query = """
    MATCH
        (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Pro|:Cons]->(y:Sentence)
    WHERE
        %s
    WITH
        count(r) as len,
        type(r) as t
    RETURN
        len
    ORDER BY
        len asc
    LIMIT
        1
    """%condition
    n_rows = int(n4j_graph.evaluate(query))
    query = """
    MATCH
        (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Pro]->(y:Sentence)
    WHERE
        %s
    WITH
        x.n as x,
        y.n as y,
        r.w as w,
        rand() as rdm
    LIMIT
        %d
    WITH
        collect({x: x, y: y, w: w, rdm: rdm}) as rows1
    MATCH
        (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Cons]->(y:Sentence)
    WHERE
        %s
    WITH
        x.n as x,
        y.n as y,
        r.w as w,
        rand() as rdm,
        rows1
    LIMIT
        %d
    WITH
        collect({x: x, y: y, w: w, rdm: rdm}) + rows1 as rows
    UNWIND
        rows as row
    RETURN
        row.x as x,
        row.y as y,
        row.w as w
    ORDER BY
        row.rdm
    """%(condition, n_rows, condition, n_rows)
    return query



def _unbalanced_dataset_query(dataset_name):
    """Cypher query for a given dataset (unbalanced classes)
    Return sentence numbers (sentence.n) for kialo
    """

    condition = _traintestdev_condition(dataset_name)
    query = """
    MATCH
        (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Pro|:Cons]->(y:Sentence)
    WHERE
        %s
    WITH
        x.n as x, y.n as y, r.w as w, rand() as rdm
    ORDER BY
        rdm
    RETURN
        x, y, w
    """%condition
    return query







if __name__ == "__main__":
    import utils
    import argparse
    import os

    DATASETS = ['train', 'dev', 'dev1', 'dev2', 'test', 'test1', 'test2']
    
    # Read command-line argument
    parser = argparse.ArgumentParser(description='Dump dataset generators on disk')
    parser.add_argument('uri', help='Neo4j uri', nargs='?', default='bolt://localhost:7687')
    parser.add_argument('user', help='Neo4j user')
    parser.add_argument('passw', help='Neo4j password')
    parser.add_argument('--unbalanced', action='store_true')
    parser.add_argument('--show_sample', action='store_true')
    parser.add_argument('--count_labels', action='store_true')
    parser.add_argument('--directory', nargs='?', default='datasets')
    args = parser.parse_args()


    # Generate and dump dataset generators
    graph = py2neo.Graph(args.uri, auth=(args.user, args.passw))
    print("Generate the 'sentence' generator", end='... ', flush=True)
    utils.dump(
        sentence_generator(graph),
        os.path.join(args.directory, 'sentences.pkl')
        )
    print("done")
    for dsname in DATASETS:
        print("Generate the '%s' dataset generator"%dsname, end='... ', flush=True)
        utils.dump(
            argument_generator(dsname, graph, balanced=(not args.unbalanced)),
            os.path.join(args.directory, "%s.pkl"%dsname)
            )
        print("done")

    # Print 10 rows of sentences and dev1 datasets (option --show_sample)
    if args.show_sample:
        for i, row in enumerate(utils.load(os.path.join(args.directory, 'sentences.pkl'))):
            if i == 10:
                break
            print(row)
        for i, row in enumerate(utils.load(os.path.join(args.directory, 'dev1.pkl'))):
            if i == 10:
                break

    # Print the dataset lengths (option --count_labels)
    if args.count_labels:
        print('dataset', 'n_rows', 'n_labels...', sep="\t")
        for dsname in DATASETS:
            labels = {}
            n = 0
            for x, y in utils.load(os.path.join(args.directory, "%s.pkl"%dsname)):
                n += 1
                try:
                    labels[y['class']] += 1
                except KeyError:
                    labels[y['class']] = 1
            print(dsname, n, *sorted(labels.items()), sep='\t')

    
