# -*- coding: utf-8 -*-

# Environment Requirements
# keras==2.3.1
# tensorflow==2.1.0
# plot_keras_history
# h5py==2.10.0

from __future__ import print_function

import numpy as np

from keras.preprocessing.text import Tokenizer, one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Reshape, Dense, Dropout, Flatten, MaxPooling1D, Input, \
    Concatenate, LSTM, Bidirectional
from keras.models import load_model

import pickle


def condition_classify(str):
    # Preparation before input

    # loading saved tokenizer
    tokenizer = Tokenizer()
    with open('condition.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    word_index = tokenizer.word_index  # A dictionary like "i" : 1 ; not necessary, but make it easier to match words with GLOVE_6B
    vocab_size = len(word_index) + 1  # Adding 1 because of reserved 0 index
    maxlen = 196
    if (len(str) > 0):
        # Single Input processing before send to model
        # get single input
        input_0 = str
        input_1 = []
        input_1.append(input_0)

        # tokenization
        input_2 = tokenizer.texts_to_sequences(input_1)

        if (len(input_2) >= maxlen):
            return "None"

        # Padding the sentences
        input_3 = pad_sequences(input_2, padding='post', maxlen=maxlen)

        bilstm_rec = load_model("situation_bilstm_recdp20_78_71.h5")
        # bilstm_rec.summary()
        y_infer = bilstm_rec.predict(input_3)

        situation = []
        categories = ['emotional', 'family', 'friendship', 'others', 'relationship', 'school', 'work'
                      ]
        for i in y_infer:
            # i=i.tolist()
            index = np.argmax(i, axis=0)
            situation.append(categories[index])
    else:
        situation = "None"

    return situation


if __name__ == '__main__':
    print(condition_classify("I have a total bad day."))