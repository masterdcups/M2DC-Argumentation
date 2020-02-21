import re
from pathlib import Path

import numpy as np
import pandas as pd

def generator_DataFrames(
        DataFrame_loaders, 
        batch_size = None, # Whole files if None, batch_size samples otherwise
        epochs = None, # Number of iterations over DataFrame_loaders
    ):
    """
        Applies a mapping to DataFrame rows, batching them into numpy arrays.

    """


    epoch = 0
    while (not epochs) or (epoch < epochs):
        epoch += 1

        for df_loader in DataFrame_loaders:
            df = df_loader()

            ## Only keep the columns we will yield.
            #df = df[[
            #    column_name 
            #    for part in mapping
            #    for column_name in mapping[part]['columns']
            #]]

            nb_samples = len(df)
            if not batch_size or batch_size > nb_samples:
                batch_size = nb_samples
            offset = 0

            while offset + batch_size <= nb_samples:
                yield df.iloc[offset:offset+batch_size]

                ## Apply the mapping.
                #batch = {
                #    part: {
                #        params.get('name', column_name): 
                #            params.get('function',default_transform)(
                #                batch[column_name]).astype(np.float32)
                #        for column_name, params 
                #            in mapping[part]['columns'].items()} 
                #    for part in mapping}

                ## Merge when needed.
                #batch = {
                #    part: 
                #        batch[part] 
                #        if not mapping[part]['parameters']['merge'] else
                #        np.concatenate(list(batch[part].values()), axis=-1)
                #    for part in mapping
                #}

                offset += batch_size

                #yield batch

