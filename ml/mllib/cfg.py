import importlib
import pathlib
import yaml

def load(yaml_path):
    return yaml.load(open(yaml_path, 'r'), yaml.FullLoader)

def load_merge(yaml_paths):
    return {
        key: values
        for yaml_path in yaml_paths
        for key, values in load(yaml_path).items()
    }

def read_pydict(pydict_path: str) -> dict:
    module_path = pathlib.Path(pydict_path)
    module = importlib.import_module(module_path.stem)

    dictionary = module.__dict__

    doc = dictionary['__doc__']

    # Select user defined components.
    dictionary = {
            key: component
            for key, component in dictionary.items()
            if not (
                (key[:2] == '__' and key[-2:] == '__') or \
                not isinstance(component, dict))                
        }

    return dictionary


def dump(objects, yaml_path):
    with open(yaml_path, 'w') as f:
        f.write(yaml.dump(objects))

