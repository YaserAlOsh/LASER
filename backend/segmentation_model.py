# Importing necessary libraries and modules.
from segmentation_main import Segmentation_main
from nsebilstm import NSEBiLSTM
import torch
import numpy as np

# Class definition for the SegmentationModel class, inheriting from Segmentation_main.
class SegmentationModel(Segmentation_main):
    def __init__(self):
        super().__init__()
        self.setup = False
        self.window_size = 5
        self.step_size = 5
        self.threshold = 0.3
        self.thresholds = {'low': 0.35, 'normal': 0.25, 'high': 0.2}

    # Method to setup the segmentation model by loading the saved state dict.
    def setup_model(self):
        self.model = NSEBiLSTM(768, 256, 2, bidirectional=True, dropout=0.5, loss_type='CrossEntropy')
        self.model.load_state_dict(torch.load('./model/bilstm_bge_auto_opt_O4_5_best_model.pt'))
        # self.model.to('cuda')
        self.model.eval()
        self.setup = True
        self.device = 'cpu'

    # Method to segment the transcript and return predicted boundaries.
    def segment_the_transcript(self, transcript, fragment_frequency='low'):
        if not self.setup:
            self.setup_model()
        windows = self.extract_window_embeddings(transcript)

        vectors = list(map(lambda x: x['vector'], windows))
        end_times = list(map(lambda x: x['end_time'], windows))

        predicted_boundaries = [0]
        with torch.no_grad():
            vectors = np.array(vectors)
            vectors = torch.FloatTensor(vectors).unsqueeze(0).to(self.device)
            outputs = self.model(vectors)
            scores = self.model.get_scores(outputs, threshold=self.thresholds[fragment_frequency])
            scores = scores.cpu().numpy()[0]  # 0 for the first batch
            predicted_boundaries = [end_times[i] for i in range(len(scores)) if scores[i]]

        return predicted_boundaries

    # Method to extract window embeddings from sentences.
    def extract_window_embeddings(self, sentences):
        embeddings = []
        for i in range(0, len(sentences) - self.window_size + 1, self.step_size):
            current_window = sentences[i:i + self.window_size]
            windows_arr = []

            for sentence in current_window:
                text = str(sentence['text'])
                windows_arr.append(text)

            start_time = current_window[-1]['start']
            end_time = current_window[-1]['end']
            window_text = ' '.join(windows_arr)
            window_representation = np.array(self.embed_sentences(window_text))
            embeddings.append({'vector': window_representation, 'end_time': end_time})
        return embeddings
