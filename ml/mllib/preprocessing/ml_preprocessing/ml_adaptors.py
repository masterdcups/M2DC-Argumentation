import numpy as np
import pandas as pd
import gensim

import functools

def fill_mapping(
        mapping, 
        default_transform = lambda x: x,
        before_transform = None,
        after_transform = None,
    ):
    # Compose a function with another : func1 o func2
    def compose(*functions):
        return functools.reduce(
                lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)),
                functions
            )

    before_functions = [] if not before_transform else [before_transform]
    after_functions = [] if not after_transform else [after_transform]

    for part, part_mapping in mapping.items():
        for stream_name, stream_mapping in part_mapping['streams'].items():
            if 'column' not in stream_mapping:
                stream_mapping['column'] = stream_name

            stream_mapping['function'] = compose(*after_functions + [
                    stream_mapping.get('function', default_transform)
                ] + before_functions)

    return mapping

def apply_mapping(mapping:dict, data: dict):
    data = {
        part: {
            stream_name:
                stream_mapping['function'](data[stream_mapping['column']])

            for stream_name, stream_mapping in mapping[part]['streams'].items()
        }
        for part in mapping
    }

    # Merge when needed.
    data = {
        part:
            data[part]
            if 'merger' not in mapping[part] else
            mapping[part]['merger'](list(data[part].values()))
        for part in mapping
    }

    return data
