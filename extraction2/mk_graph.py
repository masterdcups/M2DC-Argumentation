"""
Build the graph from the collection of csv files
"""

import os

PAGES_DIR = 'out'

def main(): 

    # Init
    edges = []
    arg_labels = {}
    arg_nums = {}
    leaf_num = 0

    def get_num(arg_id):
        """Numerical id (auto-increment)"""
        if not arg_id in arg_nums.keys():
            arg_nums[arg_id] = len(arg_nums)
        return arg_nums[arg_id]

    def get_label(arg_id):
        """Label of argument (defaults to an empty string)"""
        if not arg_id in arg_labels.keys():
            arg_labels[arg_id] = ''
        return arg_labels[arg_id]


    # Read each csv file        
    filenames = os.listdir(PAGES_DIR)
    for filename in filenames:

        # arg_id of the page (slashes was changed into tildes)
        child_id = filename.replace('.csv', '').replace('~','/')

        with open(os.path.join(PAGES_DIR, filename), 'r') as f:
            for line in f:
                parent_id, parent_label, weight = line[:-1].split(';')

                # Leaf does not have ids (i.e. does not have urls)
                if parent_id == '':
                    parent_id = 'leaf_%d'%leaf_num
                    leaf_num += 1

                # Record label
                arg_labels[parent_id] = parent_label

                # Build edge with the numerical id
                e = (get_num(parent_id), get_num(child_id), int(weight))

                # Append only non-existing edges (there is one...)
                if not e in edges:
                    edges.append(e)

    # Neo4j csvs
    with open('n4j_nodes.csv', 'w') as f:
        print('n', 'url', 'label', sep=',', file=f)
        for arg_id, arg_num in arg_nums.items():
            print(arg_num, '"'+arg_id+'"', '"'+get_label(arg_id).replace('"',"'")+'"', sep=',', file=f)
    with open('n4j_edges.csv', 'w') as f:
        print('n1', 'n2', 'weight', sep=',', file=f)
        for u,v,w in edges:
            print(u, v, w, sep=',', file=f)


    
if __name__ == "__main__":
    main()
