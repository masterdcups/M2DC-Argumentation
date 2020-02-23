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
        for column, column_mapping in part_mapping['columns'].items():
            if 'name' not in column_mapping:
                column_mapping['name'] = column

            #if 'function' not in column_mapping:
            #    column_mapping['function'] = default_transform

            #column_mapping['function'] = compose_always(
            #        column_mapping['function']))
            column_mapping['function'] = compose(*after_functions + [
                    column_mapping.get('function', default_transform)
                ] + before_functions)

        #if 'merger' in part_mapping:
        #    part_mapping['merger'] = 
        #       *[part_mapping['merger']] + before_functions)

    return mapping

def apply_mapping(mapping:dict, data: dict):
    data = {
        part: {
            column_mapping['name']:
                column_mapping['function'](data[column_name])

            for column_name, column_mapping in mapping[part]['columns'].items()
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
