import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from tqdm import tqdm

def main(xml_path, output_path):
    xml_path = Path(xml_path)
    output_path = Path(output_path)

    tokens = {}
    xml_tree = ET.parse(xml_path)
    root = xml_tree.getroot()
    for child in root:
        attrs = child.attrib
        form = attrs['form']
        if form in tokens:
            tokens[form].append(attrs)
        else:
            tokens[form] = [attrs]
    
    tokens, matrix = tokens_dict2arrays(tokens)

    np.savez(output_path,
            tokens = tokens, embeddings = matrix)


def tokens_dict2arrays(
        tokens_dict,
        oov_token='<UNK>', # 0, 0.5, 
        pad_token='<PAD>', # -1.0 norm vector
        eos_token='<EOS>', # 1.0 norm vector
    ):
    """ Embeddings of tokens to a 4D space with dimensions being:
         - polarity [-1, 1]
         - subjectivity [0, 1]
         - intensity [0.5, 2]
         - confidence [0, 1]
        These values are normalized with mean=0, std=1
    """
    features = ['polarity', 'subjectivity', 'intensity', 'confidence']
    default_vector = np.array([0.0, 0.5, 1.0, 0.0])
    default_dict = {
            feature: value
            for feature, value in zip(features, default_vector)
        } 


    nb_words, dimension = len(tokens_dict.keys()), len(features)

    if oov_token:
        nb_words += 1
    if pad_token:
        nb_words += 1
    if eos_token:
        nb_words += 1

    token_keys = sorted(tokens_dict.keys())

    words = np.zeros(nb_words, dtype=np.dtype(object))
    embeddings = np.zeros((nb_words, dimension), dtype=np.float32)



    current_word_id = 0

    if oov_token:
        words[current_word_id] = oov_token
        embeddings[current_word_id] = default_vector
        current_word_id += 1

    if pad_token:
        words[current_word_id] = pad_token
        embeddings[current_word_id] = default_vector
        #np.full(embeddings.shape[-1], value=-1.0, dtype=np.float32)
        current_word_id += 1

    if eos_token:
        words[current_word_id] = eos_token
        embeddings[current_word_id] = default_vector
        current_word_id += 1

    def mean_value(dict_list, key):
        values = list(map(
                lambda form_instance: float(
                    form_instance.get(key, default_dict[key])), 
                dict_list
            ))
        return sum(values)/len(values)
    
    for i, token_key in tqdm(enumerate(token_keys)):
        words[current_word_id] = token_key
        embeddings[current_word_id] = np.array([
                mean_value(tokens_dict[token_key], feature)
                for feature in features
            ])

        current_word_id += 1

    embeddings[:,2] -= 1.0

    return words, embeddings



if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
            description=("Transforms a textblob sentiment lexicon to numpy archive" +
            "keyed by 'tokens' and 'embeddings'.")
        )
    argparser.add_argument(
            'xml_path',
            help='path to .xml lexicon file',
        )
    argparser.add_argument(
            'output_path',
            help='path to save numpy archive (.npz) file',
        )
    args = argparser.parse_args()

    main(args.xml_path, args.output_path)
