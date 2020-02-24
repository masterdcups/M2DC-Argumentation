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
        y.label as debate,
        debn as debate_num
    ORDER BY
        rdm
    """
    for record in n4j_graph.run(query):
        yield {
            's': record['label'],
            'n': record['n'],
            'debate_name': record['debate'],
            'debate_num': record['debate_num']
            }



def argument_generator(dataset_name, n4j_graph, balanced=False):
    """Create a dataset generator that yields ({'n1':_, 'n2':_},{'class':_}) tuples.
    name: in {train, dev, dev1, dev2, test, test1, test2}
    n4j_graph: connected neo4j graph
    balanced: Return the same amout of rows for each class (edge weight)

    Available datasets:
        train: debates 0..9, 15, 17..19, 21..25
        dev: debates 14, 16, 20
        test: debates 10..13
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


def _traintestdev_debates(dataset_name):
    """Debate numbers corresponding to a dataset name

    Available datasets:
        train: debates 0..9, 15, 17..19, 21..25
        dev: debates 14, 16, 20
        test: debates 10..13
    """
    if dataset_name == "train":
        debates = list(range(10))+[15, 17, 18, 19]+list(range(21,26))
    elif dataset_name == "dev":
        debates = [14, 16, 20]
    elif dataset_name == "test":
        debates = [10, 11, 12, 13]
    else:
        raise ValueError("Dataset name must be in {train, dev, test}")
    return debates




def _balanced_dataset_query(dataset_name, n4j_graph):
    """Cypher query for a given dataset (balanced classes)
    Return sentence numbers (sentence.n) for kialo
    """

    debates = _traintestdev_debates(dataset_name)

    query = ""

    for d_num in debates:
        subquery = """
        MATCH
            (d: Debate {origin: "kl", n: %d})
        WITH
            d
        OPTIONAL MATCH
            p_pro=(d)-[:Contains]->()<-[:Pro]-()
        WITH
            d,
            count(p_pro) as n_pro
        OPTIONAL MATCH
            p_cons=(d)-[:Contains]->()<-[:Cons]-()
        WITH
            n_pro,
            count(p_cons) as n_cons
        RETURN
            CASE WHEN n_pro < n_cons THEN n_pro ELSE n_cons END as min_edges
        LIMIT
            1
        """%d_num
        
        n_rows = int(n4j_graph.evaluate(subquery))

        if query != "":
            query += " UNION "

        query += """
        MATCH
            (d: Debate {origin: "kl", n: %d})-[:Contains]->(x:Sentence)-[:Pro]->(y:Sentence)
        RETURN
            x.n as x,
            y.n as y,
            1 as w
        LIMIT
            %d
        UNION
        MATCH
            (d: Debate {origin: "kl", n: %d})-[:Contains]->(x:Sentence)-[:Cons]->(y:Sentence)
        RETURN
            x.n as x,
            y.n as y,
            -1 as w
        LIMIT
            %d
        """%(d_num, n_rows, d_num, n_rows)

    return query



def _unbalanced_dataset_query(dataset_name):
    """Cypher query for a given dataset (unbalanced classes)
    Return sentence numbers (sentence.n) for kialo
    """

    debates = _traintestdev_debates(dataset_name)
    query = """
    MATCH
        (debate:Debate {origin: "kl"})-[:Contains]->(x:Sentence)-[r:Pro|:Cons]->(y:Sentence)
    WHERE
        debate.n IN [%s]
    WITH
        x.n as x, y.n as y, r.w as w, rand() as rdm
    ORDER BY
        rdm
    RETURN
        x, y, w
    """%(', '.join(map(str, debates)))
    return query







if __name__ == "__main__":
    import utils
    import argparse
    import os

    DATASETS = ['train', 'dev', 'test']
    
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
    utils.to_csv(
        sentence_generator(graph),
        os.path.join(args.directory, 'sentences.csv')
        )
    print("done")
    for dsname in DATASETS:
        print("Generate the '%s' dataset generator"%dsname, end='... ', flush=True)
        utils.dump(
            utils.shuffle(
                argument_generator(dsname, graph, balanced=(not args.unbalanced))
                ),
            os.path.join(args.directory, "%s.pkl"%dsname)
            )
        utils.to_csv(
            utils.merge_dicts(utils.shuffle(
                argument_generator(dsname, graph, balanced=(not args.unbalanced))
                )),
            os.path.join(args.directory, "%s.csv"%dsname)
            )
        print("done")

    # Print 10 rows of sentences and dev datasets (option --show_sample)
    if args.show_sample:
        for i, row in enumerate(utils.load(os.path.join(args.directory, 'sentences.pkl'))):
            if i == 10:
                break
            print(row)
        for i, row in enumerate(utils.load(os.path.join(args.directory, 'dev.pkl'))):
            if i == 10:
                break
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
                    labels[y['class']] += 1
                except KeyError:
                    labels[y['class']] = 1
            print(dsname, n, *sorted(labels.items()), sep='\t')

    
