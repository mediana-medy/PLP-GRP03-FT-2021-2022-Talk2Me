import neattext.functions as nfx
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import pickle

# Function to preprocess dialog history and get user's risk score
def get_risk(history, username):
    # Getting all the user utterances as a series
    user_texts = []
    for utterance in history[username]:
        if utterance['speaker'] == 'usr':
            user_texts.append(utterance['text'])
    user_texts = pd.Series(user_texts)

    # Remove Stopwords
    Clean_Texts = user_texts.apply(nfx.remove_stopwords)
    # remove punctuations
    Clean_Texts = Clean_Texts.apply(nfx.remove_punctuations)

    # Concatenating text from user utterances into 1 item to get a single prediction
    combined_user_texts = ''
    for idx, text in Clean_Texts.items():
        combined_user_texts = combined_user_texts + " " + text
    combined_user_texts_series = pd.Series([combined_user_texts.strip()])

    # load model
    model = load_model('model/condition_bilstm_rec_dp.h5')

    # loading saved tokenizer
    with open('model/condition_bilstm.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # Input the combined_user_texts to the risk prediction model if it is not empty
    if combined_user_texts_series.size > 0:
        predictions = evaluate_text(model,tokenizer,combined_user_texts_series)

        risk_score = sum(predictions)/len(predictions)
    else:
        risk_score = -1

    return risk_score, combined_user_texts

# Function to input text (Series) into the risk prediction model and get the risk score
def evaluate_text(model, tokenizer, text):

    inference_sequence = tokenizer.texts_to_sequences(text)
    inference_data = pad_sequences(inference_sequence, padding='post', maxlen=70)

    predictions = model.predict(inference_data)

    return predictions
