"""
Build the graph from the collection of csv files produced by an extraction
"""

import os

class DefaultDict(dict):
    def __init__(self, default_value=None, show_warning=False, name=None):
        self.default_value = default_value
        self.show_warning = show_warning
        self.name = name
        self.count=0
    def __getitem__(self, key):
        if key in self.keys():
            return dict.__getitem__(self, key)
        if self.show_warning:
            self.count+=1
            print("Warning %s#%d: key '%s' not in dict"%(self.name,self.count,key))
        return self.default_value



def main(csvdir): 

    # Init
    edges = []
    nums = DefaultDict(-1, show_warning=True, name='nums')
    urls = {}
    labels = DefaultDict("", show_warning=True, name='labels')
    descriptions = DefaultDict("")

        

    # Read index
    with open(os.path.join(csvdir, 'index.txt'), 'r') as f:
        for line in f:
            url, num = line[:-1].split(';')
            num = int(num)
            nums[url] = num
            urls[num] = url



    # Read each csv file
    filenames = [f for f in os.listdir(csvdir) if f.endswith('.csv')]
    for filename in filenames:

        url = None
        label = None
        description = None
        num = None
        with open(os.path.join(csvdir, filename), 'r') as f:
            for line in f:
                if line.startswith('#'):
                    if line.startswith('#url: '):
                        url = line[6:-1]
                        num = nums[url]
                    elif line.startswith('#name: '):
                        label = line[6:-1].replace('"',"'").replace('\n', '<br />')
                        labels[num] = label
                    elif line.startswith('#description: '):
                        description = line[14:].replace('"',"'").replace('\n', '<br />')
                        if not num in descriptions.keys():
                            descriptions[num] = ""
                        descriptions[num] += description
                    elif line.startswith('#domain: '):
                        pass
                    else:
                        print("%s: cannot parse #-line: %s"%(filename, line[:-1]))
                else:
                    line = line[:-1].split(';')
                    if len(line) == 3:
                        parent_url, parent_label, weight = line
                    elif len(line) > 3:
                        parent_url, parent_label, weight = line[0], ';'.join(line[1:-1]), line[-1]
                    else:
                        print("%s: cannot parse line: %s"%(filename, line[:-1]))
                    weight = float(weight)
                    if parent_url == '':
                        parent_num = max(nums.values())+1
                        parent_url = "leaf_%d"%parent_num
                        nums[parent_url] = parent_num
                        urls[parent_num] = parent_url
                        labels[parent_num] = parent_label.replace('"',"'").replace('\n', '<br />')
                    else:
                        parent_num = nums[parent_url]

                    if not num == -1:
                        if not parent_num in labels.keys():
                            labels[parent_num] = parent_label.replace('"',"'").replace('\n', '<br />')
                        e = (parent_num, num, weight)
                        edges.append(e)

    # Neo4j csvs
    with open('%s_nodes.csv'%csvdir, 'w') as f:
        print('n', 'url', 'label', 'description', sep=',', file=f)
        for num, url in urls.items():
            print(num, '"'+url+'"', '"'+labels[num]+'"', '"'+descriptions[num]+'"', sep=',', file=f)
    with open('%s_edges.csv'%csvdir, 'w') as f:
        print('n1', 'n2', 'weight', sep=',', file=f)
        for u,v,w in edges:
            print(u, v, w, sep=',', file=f)


    
if __name__ == "__main__":

    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Parse the CSV files produced by an extraction and build the 'nodes' and 'edges' CSVs")
    parser.add_argument('directory')
    args = parser.parse_args()

    # Let's-a-go !
    main(args.directory)
