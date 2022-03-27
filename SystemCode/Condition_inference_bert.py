# -*- coding: utf-8 -*-

# SEED = 1
# random.seed(SEED)
# np.random.seed(SEED)
# torch.manual_seed(SEED)
# torch.backends.cudnn.deterministic = True

# !pip install keras==2.3.1
# !pip install tensorflow==2.1.0
# !pip install plot_keras_history
# !pip install h5py==2.10.0
# !pip install plot_keras_history
# !pip install transformers

"""## Import"""


from __future__ import print_function

import torch
import torch.nn as nn

from transformers import BertTokenizer, BertModel

bert = BertModel.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


class BERTGRUSentiment(nn.Module):
    def __init__(self,
                 bert,
                 hidden_dim,
                 output_dim,
                 n_layers,
                 bidirectional,
                 dropout):
        
        super().__init__()
        
        self.bert = bert
        
        embedding_dim = bert.config.to_dict()['hidden_size']
        
        self.rnn = nn.GRU(embedding_dim,
                          hidden_dim,
                          num_layers = n_layers,
                          bidirectional = bidirectional,
                          batch_first = True,
                          dropout = 0 if n_layers < 2 else dropout)
        
        self.out = nn.Linear(hidden_dim * 2 if bidirectional else hidden_dim, output_dim)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text):
        
        #text = [batch size, sent len]
                
        with torch.no_grad():
            embedded = self.bert(text)[0]
                
        #embedded = [batch size, sent len, emb dim]
        
        _, hidden = self.rnn(embedded)
        
        #hidden = [n layers * n directions, batch size, emb dim]
        
        if self.rnn.bidirectional:
            hidden = self.dropout(torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim = 1))
        else:
            hidden = self.dropout(hidden[-1,:,:])
                
        #hidden = [batch size, hid dim]
        
        output = self.out(hidden)
        
        #output = [batch size, out dim]
        
        return output


def categorical_accuracy(preds, y):
    """
    Returns accuracy per batch, i.e. if you get 8/10 right, this returns 0.8, NOT 8
    """
    max_preds = preds.argmax(dim = 1, keepdim = True) # get the index of the max probability
    correct = max_preds.squeeze(1).eq(y)
    # correct.to(device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
    return correct.sum() / len(correct)

def evaluate(model, iterator, criterion):
    
    epoch_loss = 0
    epoch_acc = 0
    
    model.eval()
    
    with torch.no_grad():
      for batch in iterator:
  
          
          predictions = model(batch.text).squeeze(1)
          
          loss = criterion(predictions, batch.label)
          
          acc = categorical_accuracy(predictions, batch.label)
          

          
          epoch_loss += loss.item()
          epoch_acc += acc.item()
        
    return epoch_loss / len(iterator), epoch_acc / len(iterator)


categories=['emotional','work','relationship','friendship','school','others','family']

HIDDEN_DIM = 256
OUTPUT_DIM = 7
N_LAYERS = 2
BIDIRECTIONAL = True
DROPOUT = 0.25
max_input_length = 512
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = BERTGRUSentiment(bert,
                         HIDDEN_DIM,
                         OUTPUT_DIM,
                         N_LAYERS,
                         BIDIRECTIONAL,
                         DROPOUT)

init_token = tokenizer.cls_token
eos_token = tokenizer.sep_token
pad_token = tokenizer.pad_token
unk_token = tokenizer.unk_token

init_token_idx = tokenizer.convert_tokens_to_ids(init_token)
eos_token_idx = tokenizer.convert_tokens_to_ids(eos_token)
pad_token_idx = tokenizer.convert_tokens_to_ids(pad_token)
unk_token_idx = tokenizer.convert_tokens_to_ids(unk_token)
max_input_length = tokenizer.max_model_input_sizes['bert-base-uncased']

model.load_state_dict(torch.load("tut6-model.pt"))
model = model.to(device)

def predict_sentiment(sentence):
    model.eval()
    tokens = tokenizer.tokenize(sentence)
    tokens = tokens[:max_input_length-2]
    indexed = [init_token_idx] + tokenizer.convert_tokens_to_ids(tokens) + [eos_token_idx]
    tensor = torch.LongTensor(indexed).to(device)
    tensor = tensor.unsqueeze(0)
    prediction = torch.sigmoid(model(tensor))
    index = torch.argmax(prediction)
    label = categories[index.cpu().numpy()]
    return label


if __name__ == '__main__':
    predict_sentiment("I have totally a bad day")