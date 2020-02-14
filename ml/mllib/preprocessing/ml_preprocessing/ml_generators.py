import re
from pathlib import Path

import numpy as np
import pandas as pd

def generator_DataFrame2numpy(
        DataFrame_loaders, 
        mapping,
        batch_size = None, # Whole files if None, batch_size samples otherwise
        epochs = 1, # Number of iterations over DataFrame_loaders
        default_transform = lambda column: column.values[:, None],
    ):
    """
        Applies a mapping to DataFrame rows, batching them into numpy arrays.


        Parameters:

         - mapping: dictionary with the following structure:

        ```
            # 'str' keys (e.g.: 'columns') are used by mapper, 
            # while str keys (e.g.: column_name) are to be defined by mapping.
            {
                part: {
                    'columns': {
                        column_name: {
                            'function': func, # defaults to default_to_numpy
                            'name': renamed_column, # defaults to column_name
                        },
                    },
                    'parameters': {
                        'merge': bool
                    }
                }
            }
        ```
        See feature_transformers.default_DataFrame2numpy_mapping() for an
        example.
    
        Returns:
         - dictionary with the following structure:

        ```
            {
                part_not_merged: {
                    renamed_column: func(DataFrame[column_name])
                }

                # All columns of the part are concatenated.
                part_merged: np.concatenate([part[renamed_column]])
            }
        ```

    """



    for epoch in range(epochs):
        for df_loader in DataFrame_loaders:
            df = df_loader()

            # Only keep the columns we will yield.
            df = df[[
                column_name 
                for part in mapping
                for column_name in mapping[part]['columns']
            ]]

            nb_samples = len(df)
            if not batch_size or batch_size > nb_samples:
                batch_size = nb_samples
            offset = 0

            while offset + batch_size <= nb_samples:
                batch = df.iloc[offset:offset+batch_size]

                # Apply the mapping.
                batch = {
                    part: {
                        params.get('name', column_name): 
                            params.get('function',default_transform)(
                                batch[column_name])
                        for column_name, params 
                            in mapping[part]['columns'].items()} 
                    for part in mapping}

                # Merge when needed.
                batch = {
                    part: 
                        batch[part] 
                        if not mapping[part]['parameters']['merge'] else
                        np.concatenate(list(batch[part].values()), axis=-1)
                    for part in mapping
                }

                offset += batch_size

                yield batch

