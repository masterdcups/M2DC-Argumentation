"""
Module: datasets

Generate kialo datasets from the neo4j database.
 - as a module: *create_dataset* returns a dataset generator
 - as a script: the script outputs all dataset generators using utils.dump

"""
import py2neo




def create_dataset(dataset_name, n4j_graph, balanced=True):
    """Create a dataset generator that yields ((text1,text2),weight) tuples.
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



    
    if balanced:
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
            x.label as x,
            y.label as y,
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
            x.label as x,
            y.label as y,
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

    else:
        query = """
        MATCH
            (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Pro|:Cons]->(y:Sentence)
        WHERE
            %s
        WITH
            x.label as x, y.label as y, r.w as w, rand() as rdm
        ORDER BY
            rdm
        RETURN
            x, y, w
        """%condition

    for record in n4j_graph.run(query):
        yield (record['x'], record['y']), record['w']




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
    for dsname in DATASETS:
        print("Generate the '%s' dataset generator"%dsname, end='... ', flush=True)
        utils.dump(
            create_dataset(dsname, graph, balanced=(not args.unbalanced)),
            os.path.join(args.directory, "%s.pkl"%dsname)
            )
        print("done")

    # Print the dev1 dataset (option --show_sample)
    if args.show_sample:
        for row in utils.load(os.path.join(args.directory, 'dev1.pkl')):
            print(row)

    # Print the dataset lengths (option --count_labels)
    if args.count_labels:
        print('dataset', 'n_rows', 'n_labels...', sep="\t")
        for dsname in DATASETS:
            labels = {}
            n = 0
            for x, y in utils.load(os.path.join(args.directory, "%s.pkl"%dsname)):
                n += 1
                try:
                    labels[y] += 1
                except KeyError:
                    labels[y] = 1
            print(dsname, n, *sorted(labels.items()), sep='\t')

    
