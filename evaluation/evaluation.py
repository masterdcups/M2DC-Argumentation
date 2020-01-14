import numpy as np
import networkx as nx

"""
    Deg_Ebs(a) = 1 - ( (1 - w(a)²) / (1 + w(a)e^E) )
    E = Sum over x in Supp(a) (Deg_Ebs(x)) - Sum over x in Att(a) (Deg_Ebs(x))
"""
def evaluate(argument_dag):
    """
        Evaluates an argument graph according to Euler-based semantic,
        as defined in the paper titled: 
        "Weighted Bipolar Argumentation Graphs: Axioms and Semantics"
        (Amgoud & Ben-Naim)

        Nodes (arguments) should have a "strength" property and edges
        a "polarity" property (in ["attack", "support"]).

        Returns a dictionary mapping argument names to their overall strength.
    """
    ordering = nx.topological_sort(argument_dag)

    overall_strength = {}

    for target in ordering:
        w = argument_dag.nodes[target]['strength']

        in_edges = argument_dag.in_edges(target, 'polarity')
        E = sum([
            overall_strength[edge[0]]
            if edge[2] == 'support' else
            -overall_strength[edge[0]]
            for edge in in_edges
        ])

        overall_strength[target] = (
            1 - ( (1 - w**2) / (1 + w * np.exp(E)) )
        )

    return overall_strength

# Returns the graph from the 5th page of 
# "Weighted Bipolar Argumentation Graphs: Axioms and Semantics" 
# by Leila Amgoud, Jonathan Ben-Naim
def sample_graph():
    nodes = [
        ('a', {'strength': 0.60}),
        ('b', {'strength': 0.60}),
        ('c', {'strength': 0.60}),
        ('d', {'strength': 0.22}),
        ('e', {'strength': 0.40}),
        ('f', {'strength': 0.40}),
        ('g', {'strength': 0.00}),
        ('h', {'strength': 0.99}),
        ('i', {'strength': 0.10}),
        ('j', {'strength': 0.99}),
    ]

    edges_attack = [
        ('d', 'a'),
        ('d', 'b'),
        ('e', 'b'),
        ('e', 'c'),
        ('f', 'c'),
        ('g', 'e'),
        ('h', 'f'),
    ]
    edges_support = [
        ('i', 'a'),
        ('i', 'b'),
        ('i', 'c'),
        ('j', 'i'),
    ]
    graph = nx.DiGraph()
    
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges_attack, polarity='attack')
    graph.add_edges_from(edges_support, polarity='support')
    
    return graph

def main():
    graph = sample_graph()

    overall_strength = evaluate(graph)
    
    print("{:<20}{:<20}".format("Argument", "Strength"))
    for argument_name, argument_strength in overall_strength.items():
        print("{:<20}{:<20.2f}".format(
            argument_name, argument_strength
        ))

if __name__ == '__main__':
    main()
