# Importing necessary libraries and modules.
import torch
import torch.nn as nn

# Definition of the NSEBiLSTM neural network class.
class NSEBiLSTM(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, n_layers, bidirectional=True, dropout=0.5, loss_type='CrossEntropy'):
        super(NSEBiLSTM, self).__init__()

        # BERT Encoder (commented out)
        # self.encoder = encoder  # BertModel.from_pretrained('bert-base-uncased')
        # self.tokenizer = tokenizer  # BertTokenizer.from_pretrained('bert-base-uncased')

        # Initialization of BiLSTM parameters
        self.hidden_dim = hidden_dim
        self.loss_type = loss_type

        # BiLSTM layer
        self.bilstm = nn.LSTM(input_size=embedding_dim,
                              hidden_size=hidden_dim,
                              num_layers=n_layers,
                              bidirectional=bidirectional,
                              dropout=(0 if n_layers == 1 else dropout),
                              batch_first=True)

        # Output layer setup based on loss type
        if loss_type == 'CrossEntropy' or loss_type == 'CE':
            self.fc = nn.Linear(hidden_dim * 2 if bidirectional else hidden_dim, 2)
            self.bce = False
            self.loss_fn = nn.CrossEntropyLoss(ignore_index=-1)
            self.act = nn.Softmax(dim=2)
        elif loss_type == 'BinaryCrossEntropy' or loss_type == 'BCE':
            self.fc = nn.Linear(hidden_dim * 2 if bidirectional else hidden_dim, 1)
            self.bce = True
            self.act = nn.Sigmoid()
            self.loss_fn = nn.BCELoss()

    def forward(self, sentences_embeddings, mask=None):
        # Pass embeddings through BiLSTM
        lstm_out, _ = self.bilstm(sentences_embeddings)
        
        # Apply mask if provided
        if mask is not None:
            lstm_out = lstm_out * mask.unsqueeze(-1)

        # Feedforward through the output layer
        dense_outputs = self.fc(lstm_out)
        outputs = dense_outputs

        return outputs

    def get_boundaries(self, outputs, threshold=0.5):
        # Extract boundaries based on the output probabilities
        boundaries = [i for i in range(len(outputs)) if outputs[i] > threshold]
        return boundaries

    def get_scores(self, logits, threshold=None):
        # Return scores based on the specified loss type
        if self.loss_type == 'CrossEntropy' or self.loss_type == 'CE':
            if threshold is not None:
                return self.act(logits)[:, :, 1] > threshold
            return torch.argmax(self.act(logits), dim=2)
        else:
            return self.act(logits)
