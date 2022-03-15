# coding=utf-8

import json
import shutil
import pickle
import os
import logging
import multiprocessing as mp
from os.path import dirname, exists, join
import torch
import tqdm
from inputters import strat
from utils.building_utils import build_model

config_name = "strat"
inputter_name = "strat"
train_input_file = "train.txt"
max_input_length = 160
max_decoder_input_length = 40

names = {
    'inputter_name': inputter_name,
    'config_name': config_name,
}

inputter = strat
toker = build_model(only_toker=True, **names)

with open(train_input_file) as f:
    reader = f.readlines()

if not os.path.exists(f'./DATA'):
    os.mkdir(f'./DATA')
save_dir = f'./DATA/{inputter_name}.{config_name}'
if not exists(save_dir):
    os.mkdir(save_dir)

kwargs = {
    'max_input_length': max_input_length,
    'max_decoder_input_length': max_decoder_input_length,
    'max_knowledge_length': None,
    'label_num': None,
    'only_encode': True,
}

def process_data(line):
    data = json.loads(line)
    inputs = inputter.convert_data_to_inputs(
        data=data,
        toker=toker,
        **kwargs
    )
    features = inputter.convert_inputs_to_features(
        inputs=inputs,
        toker=toker,
        **kwargs,
    )
    return features

processed_data = []
for features in map(process_data, tqdm.tqdm(reader, total=len(reader))):
    processed_data.extend(features)

# save data
data_path = f'{save_dir}/data.pkl'
with open(data_path, 'wb') as file:
    pickle.dump(processed_data, file)
kwargs.update({'n_examples': len(processed_data)})
# save relevant information to reproduce
with open(f'{save_dir}/meta.json', 'w') as writer:
    json.dump(kwargs, writer, indent=4)
torch.save(toker, f'{save_dir}/tokenizer.pt')
