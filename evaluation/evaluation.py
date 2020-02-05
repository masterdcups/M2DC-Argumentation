import numpy as np
import networkx as nx

"""
"""
def evaluate(argument_dag, dag=False, max_iterations=100, epsilon=1e-6,
        verbose=False):
    """
        Evaluates an argument graph according to Euler-based semantic,
        as defined in the paper titled: 
        "Weighted Bipolar Argumentation Graphs: Axioms and Semantics"
        (Amgoud & Ben-Naim)

        Nodes (arguments) should have a "weight" property and edges
        a "weight" property encoding the polarity in [-1, 1].

        The algorithm can either evaluate the arguments in their topological
        order (if dag=True), or evaluate until convergence is reached.

        Returns a dictionary mapping argument names to their overall strength.

        The formula for computing the Euler-based semantic evaluation is given
        as:
            Deg_Ebs(a) = 1 - ( (1 - w(a)²) / (1 + w(a)e^E) )
            E = Sum over x in Supp(a) (Deg_Ebs(x)) 
              - Sum over x in Att(a) (Deg_Ebs(x))
    """

    if dag:
        intrinsic_strength = {
            argument: argument_dag.nodes[argument]['weight']
            for argument in argument_dag.nodes()
        }
        overall_strength = {
            argument: argument_dag.nodes[argument]['weight']
            for argument in argument_dag.nodes()
        }
        ordering = list(nx.topological_sort(argument_dag))

        # Compute Euler-based evaluation of arguments
        for target in ordering:
            in_edges = argument_dag.in_edges(target, True)

            # Add up the strength of all supporters and attackers.
            E = sum([
                overall_strength[edge[0]] * edge[2]['weight']
                for edge in in_edges
            ])
            w = intrinsic_strength[target]

            new_w = 1 - ( (1 - w**2) / (1 + w * np.exp(E)) )
            
            overall_strength[target] = new_w

        evaluated_strength = overall_strength

    # Use the convergence algorithm.
    else:
        intrinsic_strength = np.array([
            argument_dag.nodes[node]['weight'] 
            for node in argument_dag.nodes()])
        overall_strength = np.copy(intrinsic_strength)
        adjacency_matrix = nx.to_numpy_array(argument_dag)

        delta = epsilon + 1
        i = 0
        while delta >= epsilon and i < max_iterations:
            delta = overall_strength

            E = np.dot(overall_strength, adjacency_matrix)

            overall_strength = (
                1 - ( 
                    (1 - intrinsic_strength**2) 
                    / 
                    (1 + intrinsic_strength * np.exp(E)) 
                )
            )

            delta = np.sum(np.abs(delta - overall_strength))
            i += 1

        evaluated_strength = {
            argument: overall_strength[i]
            for i, argument in enumerate(argument_dag.nodes())
        }

        if verbose:
            print("Done in {} iterations. Delta = {:.6f}".format(i, delta))


    return evaluated_strength

# Returns the graph from the 5th page of 
# "Weighted Bipolar Argumentation Graphs: Axioms and Semantics" 
# by Leila Amgoud, Jonathan Ben-Naim
def sample_graph():
    nodes = [
        ('a', {'weight': 0.60}),
        ('b', {'weight': 0.60}),
        ('c', {'weight': 0.60}),
        ('d', {'weight': 0.22}),
        ('e', {'weight': 0.40}),
        ('f', {'weight': 0.40}),
        ('g', {'weight': 0.00}),
        ('h', {'weight': 0.99}),
        ('i', {'weight': 0.10}),
        ('j', {'weight': 0.99}),
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
    graph.add_edges_from(edges_attack, polarity='attack', weight=-1)
    graph.add_edges_from(edges_support, polarity='support', weight=1)
    
    return graph

def main():
    graph = sample_graph()

    overall_strength = evaluate(graph, dag=False, verbose=True)
    
    print("{:<20}{:<20}".format("Argument", "Strength"))
    for argument_name, argument_strength in overall_strength.items():
        print("{:<20}{:<20.2f}".format(
            argument_name, argument_strength
        ))

if __name__ == '__main__':
    main()
