"""
Show stats on a given dataset

Use -h option for usage
"""
import utils

def count_labels(iterable):
    """Label frequency (dict)"""
    labels = {}
    for x, y in iterable:
        try:
            labels[y['class']] += 1
        except KeyError:
            labels[y['class']] = 1
    return labels


if __name__ == "__main__":


    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Count label frequency')
    parser.add_argument('filename', nargs='+')
    args = parser.parse_args()



    # CSV-like format
    print('dataset', 'n_rows', 'n_-1', 'n_1', sep="\t") 
    for filename in args.filename:
        dataset = utils.load(filename)
        labels = count_labels(dataset)
        print(filename, sum(labels.values()), labels[-1.], labels[1.], sep="\t")

