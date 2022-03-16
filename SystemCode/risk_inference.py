# Load Text Cleaning Pkgs
import neattext.functions as nfx

import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import pickle

def get_risk(history):

    user_texts = []
    for utterance in history['dialog']:
        if utterance['speaker'] == 'usr':
            user_texts.append(utterance['text'])
    user_texts = pd.Series(user_texts)

    # Remove Stopwords
    Clean_Texts = user_texts.apply(nfx.remove_stopwords)
    # remove punctuations
    Clean_Texts = Clean_Texts.apply(nfx.remove_punctuations)

    # load model
    model = load_model('model/condition_bilstm_rec_dp.h5')

    # loading saved tokenizer
    tokenizer = Tokenizer()
    with open('condition.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    if Clean_Texts.size > 0:
        predictions = evaluate_text(model,tokenizer,Clean_Texts)

        risk_score = sum(predictions)/len(predictions)
    else:
        risk_score = -1

    return risk_score

def evaluate_text(model, tokenizer, text):

    inference_sequence = tokenizer.texts_to_sequences(text)
    inference_data = pad_sequences(inference_sequence, padding='post', maxlen=70)

    predictions = model.predict(inference_data)

    return predictions
