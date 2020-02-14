import yaml

def load(yaml_path):
    return yaml.load(open(yaml_path, 'r'), yaml.FullLoader)

def load_merge(yaml_paths):
    return {
        key: values
        for yaml_path in yaml_paths
        for key, values in load(yaml_path).items()
    }

def dump(objects, yaml_path):
    with open(yaml_path, 'w') as f:
        f.write(yaml.dump(objects))

