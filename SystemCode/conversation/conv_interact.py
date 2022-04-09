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
       self.single_turn = False
       self.max_input_length = 256
       self.max_src_turn=20
       self.max_decoder_input_length = 64
       self.max_knl_len = 64
       self.label_num = None


def chat_conv(msg, history, username):
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
    #history = {'dialog': [], }

    # Conversation strategies for early, mid, late conversation stages
    strategies_1 = ["Question", "Restatement or Paraphrasing", "Reflection of feelings", "Self-disclosure"]
    strategies_2 = ["Reflection of feelings", "Self-disclosure", "Affirmation and Reassurance", "Others"]
    strategies_3 = ["Self-disclosure", "Affirmation and Reassurance", "Providing Suggestions", "Information", "Others"]

    while True:
        try:
            if args.single_turn and len(history[username]) > 0:
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
                if len(history[username]) > 0:
                    with open(os.path.join(output_dir, save_name + '.json'), 'w') as f:
                        json.dump(history, f, ensure_ascii=False, indent=2)
            except PermissionError as e:
                pass

            history = {'dialog': [], }
            print('\n\nA new conversation starts!')
            continue

        history[username].append({
            'text': _norm(msg),
            'speaker': 'usr',
        })

        # for the first 3 user utterances, take a strategy from strategies_1 list
        if len(history[username]) < 7:
            print("Le")
            strategy = random.choice(strategies_1)
        # for the next 3 user utterances, take a strategy from strategies_2 list
        elif len(history[username]) > 6 and len(history[username]) < 13:
            print("mid")
            strategy = random.choice(strategies_2)
        # for 7th and after user utterances, take a strategy from strategies_3 list
        else:
            print("end")
            strategy = random.choice(strategies_3)

        # generate response
        history[username].append({  # dummy tgt
            'text': 'n/a',
            'speaker': 'sys',
            'strategy': strategy,
        })

        inputs = inputter.convert_data_to_inputs(history[username], toker, **dataloader_kwargs)
        inputs = inputs[-1:]
        features = inputter.convert_inputs_to_features(inputs, toker, **dataloader_kwargs)
        batch = inputter.prepare_infer_batch(features, toker, interact=True)
        batch = {k: v.to(device) if isinstance(v, Tensor) else v for k, v in batch.items()}
        batch.update(generation_kwargs)
        encoded_info, generations = model.generate(**batch)

        out = generations[0].tolist()
        out = cut_seq_to_eos(out, eos)
        text = toker.decode(out).encode('ascii', 'ignore').decode('ascii').strip()

        history[username].pop()
        history[username].append({
            'text': text,
            'speaker': 'sys',
            'strategy': strategy,
        })

        return "AI: " + text


