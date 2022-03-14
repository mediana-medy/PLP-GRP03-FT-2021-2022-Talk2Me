# from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
#
# mname = "facebook/blenderbot-400M-distill"
# model = BlenderbotForConditionalGeneration.from_pretrained(mname)
# tokenizer = BlenderbotTokenizer.from_pretrained(mname)
# UTTERANCE = "My friends are cool but they eat too many carbs."
# inputs = tokenizer([UTTERANCE], return_tensors="pt")
# reply_ids = model.generate(**inputs)
# print(tokenizer.batch_decode(reply_ids))

# coding=utf-8

import json
import datetime
import torch
from torch import Tensor
import numpy as np
import os
import logging
import argparse
import random

from transformers.trainer_utils import set_seed
from SystemCode.conversation.utils.building_utils import boolean_string, build_model, deploy_model
from SystemCode.conversation.inputters import inputters
from SystemCode.conversation.inputters.inputter_utils import _norm


def cut_seq_to_eos(sentence, eos, remove_id=None):
    if remove_id is None:
        remove_id = [-1]
    sent = []
    for s in sentence:
        if s in remove_id:
            continue
        if s != eos:
            sent.append(s)
        else:
            break
    return sent


class Args():
   def __init__(self):
       self.config_name = 'strat'
       self.inputter_name = 'strat'
       self.seed = 3
       self.load_checkpoint = 'conversation/checkpoint_/epoch-1.bin'
       self.fp16 = False
       self.max_src_len = 150
       self.max_tgt_len = 50
       self.max_length = 50
       self.min_length = 10
       self.temperature = 0.7
       self.top_k = 0
       self.top_p = 0.9
       self.num_beams = 1
       self.repetition_penalty = 1
       self.no_repeat_ngram_size = 3
       self.use_gpu = True
       self.single_turn = True
       self.max_input_length = 256
       self.max_src_turn=20
       self.max_decoder_input_length = 64
       self.max_knl_len = 64
       self.label_num = None


def chat_conv(msg):
    args = Args()

    device = torch.device("cuda" if torch.cuda.is_available() and args.use_gpu else "cpu")
    n_gpu = torch.cuda.device_count()
    args.device, args.n_gpu = device, n_gpu

    if args.load_checkpoint is not None:
        output_dir = args.load_checkpoint + '_interact_dialogs'
    else:
        os.makedirs('./DEMO', exist_ok=True)
        output_dir = './DEMO/' + args.config_name
        if args.single_turn:
            output_dir = output_dir + '_1turn'
    os.makedirs(output_dir, exist_ok=True)

    # set_seed(args.seed)
    names = {
        'inputter_name': args.inputter_name,
        'config_name': args.config_name,
    }

    toker, model, *_ = build_model(checkpoint=args.load_checkpoint, **names)
    model = deploy_model(model, args)

    model.eval()

    inputter = inputters[args.inputter_name]()
    dataloader_kwargs = {
        'max_src_turn': args.max_src_turn,
        'max_input_length': args.max_input_length,
        'max_decoder_input_length': args.max_decoder_input_length,
        'max_knl_len': args.max_knl_len,
        'label_num': args.label_num,
    }

    pad = toker.pad_token_id
    if pad is None:
        pad = toker.eos_token_id
        assert pad is not None, 'either pad_token_id or eos_token_id should be provided'
    bos = toker.bos_token_id
    if bos is None:
        bos = toker.cls_token_id
        assert bos is not None, 'either bos_token_id or cls_token_id should be provided'
    eos = toker.eos_token_id
    if eos is None:
        eos = toker.sep_token_id
        assert eos is not None, 'either eos_token_id or sep_token_id should be provided'

    generation_kwargs = {
        'max_length': args.max_length,
        'min_length': args.min_length,
        'do_sample': True if (args.top_k > 0 or args.top_p < 1) else False,
        'temperature': args.temperature,
        'top_k': args.top_k,
        'top_p': args.top_p,
        'num_beams': args.num_beams,
        'repetition_penalty': args.repetition_penalty,
        'no_repeat_ngram_size': args.no_repeat_ngram_size,
        'pad_token_id': pad,
        'bos_token_id': bos,
        'eos_token_id': eos,
    }

    eof_once = False
    history = {'dialog': [], }

    strategies = ["Question", "Affirmation and Reassurance", "Information", "Self-disclosure", "Providing Suggestions",
                  "Restatement or Paraphrasing", "Others"]

    while True:
        try:
            if args.single_turn and len(history['dialog']) > 0:
                raise EOFError
            while not msg:
                return "invalid"
            eof_once = False
        except (EOFError, KeyboardInterrupt) as e:
            if eof_once:
                raise e
            eof_once = True
            save_name = datetime.datetime.now().strftime('%Y-%m-%d%H%M%S')
            try:
                if len(history['dialog']) > 0:
                    with open(os.path.join(output_dir, save_name + '.json'), 'w') as f:
                        json.dump(history, f, ensure_ascii=False, indent=2)
            except PermissionError as e:
                pass

            history = {'dialog': [], }
            print('\n\nA new conversation starts!')
            continue

        history['dialog'].append({
            'text': _norm(msg),
            'speaker': 'usr',
        })


        strategy = random.choice(strategies)
        # generate response
        history['dialog'].append({  # dummy tgt
            'text': 'n/a',
            'speaker': 'sys',
            'strategy': strategy,
        })
        inputs = inputter.convert_data_to_inputs(history, toker, **dataloader_kwargs)
        inputs = inputs[-1:]
        features = inputter.convert_inputs_to_features(inputs, toker, **dataloader_kwargs)
        batch = inputter.prepare_infer_batch(features, toker, interact=True)
        batch = {k: v.to(device) if isinstance(v, Tensor) else v for k, v in batch.items()}
        batch.update(generation_kwargs)
        encoded_info, generations = model.generate(**batch)

        out = generations[0].tolist()
        out = cut_seq_to_eos(out, eos)
        text = toker.decode(out).encode('ascii', 'ignore').decode('ascii').strip()

        history['dialog'].pop()
        history['dialog'].append({
            'text': text,
            'speaker': 'sys',
            'strategy': strategy,
        })

        return "AI: " + text


