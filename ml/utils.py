"""
Utils
"""

import pickle as pkl


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

def gmap(generator, f):
    """Map the function 'f' to every item of the generator"""
    for item in generator:
        yield f(item)
    


if __name__ == "__main__":

    # Read command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Sample run')
    parser.add_argument('filename', nargs="?", default="sample_run.pkl")
    args = parser.parse_args()

    # Sample run
    generator = ((i, 100-i, i**2) for i in range(100))
    generator = gmap(generator, lambda t: (t[0], t[1], t[2], t[0]+t[1]))
    dump(generator, args.filename)
    for row in load(args.filename):
        print(row)
