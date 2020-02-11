"""
Utils
"""

import pickle as pkl
import pandas as pd


def dump(generator, filename):
    """Dump a generator on disk"""
    with open(filename, 'wb') as f:
        for row in generator:
            pkl.dump(row, f)

def load(filename):
    """Load a generator from disk"""
    with open(filename, 'rb') as f:
        while True:
            try:
                yield pkl.load(f)
            except EOFError as e:
                return None

def print_items(generator):
    """Print each row and yield it"""
    for row in generator:
        print(row)
        yield row

def gmap(generator, f):
    """Map the function 'f' to every item of the generator"""
    for item in generator:
        yield f(item)
    

def merge_dicts(generator):
    """Merge yielded items: some dicts with distinct keys -> a dict with all keys"""
    for item in generator:
        record = {}
        for d in item:
            for k,v in d.items():
                record[k] = v
        yield record

def split_dicts(generator, *key_lists):
    """Split yielded items in dicts corresponding to the given key lists"""
    for item in generator:
        item2 = []
        for key_list in key_lists:
            item2.append({k: item[k] for k in key_list})
        yield tuple(item2)



def to_csv(generator, filename=None):
    """CSV of a generator that yields dicts"""
    return pd.DataFrame(list(generator)).to_csv(filename)
    

def from_csv(filename):
    """Read a csv and return a generator that yield dicts correspnding to columns"""
    df = pd.read_csv(filename)
    columns = list(df.columns)
    for row in df.to_records(index=False):
        yield {columns[i]: row[i] for i in range(1, len(row))}


if __name__ == "__main__":

    # Read command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Sample run')
    parser.add_argument('filename', nargs="?", default="sample_run")
    args = parser.parse_args()

    # Create generator
    generator = ((i, 100-i, i**2) for i in range(100))
    # Map generator with a function that produces a tuple of 2 dicts
    generator = gmap(generator, lambda t: ({'x0':t[0], 'x1':t[1], 'x0^2':t[2]}, {'x0+x1':t[0]+t[1]}))
    # Dump th generator with its structure
    dump(generator, args.filename+'.pkl')
    # Load the dumped generator
    generator = load(args.filename+'.pkl')
    # Inline-print of items
    #generator = print_items(generator)
    # Merge the 2 dicts of tuples into one
    generator = merge_dicts(generator)
    # Save a CSV corresponding to the generator
    to_csv(generator, args.filename+'.csv')
    # Load the CSV
    generator = from_csv(args.filename+'.csv')
    # Split the yielded dicts
    generator = split_dicts(generator, ['x0','x1'],['x0^2'], ['x0+x1'])

    # Print output    
    for row in generator:
        print(row)
