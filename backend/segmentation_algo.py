### importing required libraries
from segmentation_main import Segmentation_main
from scipy.spatial.distance import cosine
from scipy.signal import find_peaks
import numpy as np
import torch
import json

"""
A class used to segment a video based on transcripts in a "json file format"

Attributes:
-----------
cue_representations_c_windows : list
    a list that contains the vector of each sentence then calculates the average of vectors in a window
window_size : int
    number of windows that the transcript needs to split itself
step_size : int 
    takes the window size and divided it by 6 to make it move across the entire transcript
cosine_similarities : list
    stores the differences between each window by calculating the cosine
k_value : int
    a number that can be selected as a boundary of the fragments
m_value : int
    a multiplier that is in the threshold function

Methods:
-----------
extract_sentences(string)
    extracts each sentence found in the json file and transform it to a vector representation
    and stores this vector in a list
calculate_similarities()
    calculate the difference between the current and next window using the cosine similarity function
segment_the_transcript()
    a function that calls different methods to store the segments in a list
    returns a list of segments "in seconds"
calculate_the_depth_values(list, list, list, list)
    calculate the depth value using a formula discussed in a paper
    returns a list of depth values "sorted"
get_the_fragments(list, float)
    checks whether the depth value is greater than the threshold or not
    if yes:
        append it to a list
    return this list
calculate_threshold(list, list)
    calculates the threshold using the threshold formula that is in the paper
    return threshold
calculate_the_valleys_and_peaks()
    caculate the values and peaks based on the cosine similarties
    returns the following lists:
        cosine similarities vals, signal, valleys, valleys_array, peaks
"""
class Segmentation_algo(Segmentation_main):
    def __init__(self) -> None:
        super().__init__()

    def reset(self, video_duration):
        # Reset attributes based on the video duration
        self.cue_representations_c_windows = []
        self.window_size = 5
        self.step_size = self.window_size
        self.cosine_similarities = []
        if video_duration > 1800:
            self.k_value = 10  # 3, 5, 7, 10 => 600s
        elif video_duration > 1200 and video_duration <= 1800:
            self.k_value = 7
        else:
            self.k_value = 5
        self.m_value = 1

    def extract_sentences(self, sentences):
        # Extract sentences from the json file and transform them into vector representations
        for i in range(0, len(sentences) - self.window_size + 1, self.step_size):
            # Extract the current window
            current_window = sentences[i:i + self.window_size]
            windows_arr = []

            for sentence in current_window:
                text = str(sentence['text'])
                windows_arr.append(text)

            start_time = current_window[-1]['start']
            end_time = current_window[-1]['end']
            window_text = ' '.join(windows_arr)
            window_representation = np.array(self.embed_sentences(window_text))
            self.cue_representations_c_windows.append({'vector': window_representation, 'end_time': end_time})

    def calculate_similarities(self):
        # Calculate cosine similarities between consecutive windows
        for x in range(len(self.cue_representations_c_windows)-1):
            current_window_representation = self.cue_representations_c_windows[x]['vector']
            next_window_representation = self.cue_representations_c_windows[x+1]['vector']
            similarity = cosine(current_window_representation, next_window_representation)
            self.cosine_similarities.append({'similarity': similarity, 'end_time': self.cue_representations_c_windows[x]['end_time']})

    def segment_the_transcript(self, transcript_chunks, video_duration):
        # Segment the transcript into fragments
        self.reset(video_duration=video_duration)
        self.extract_sentences(transcript_chunks)
        self.calculate_similarities()
        cosine_similarities_vals, signal, valleys, valleys_array, peaks = self.calculate_the_valleys_and_peaks()
        depth_val = self.calculate_the_depth_values(cosine_similarities_vals=cosine_similarities_vals, valleys=valleys, valleys_array=valleys_array, peaks=peaks)
        threshold = self.calculate_threshold(cosine_similarities_vals=cosine_similarities_vals, valleys=valleys)
        fragment_boundaries = self.get_the_fragments(depth_val=depth_val, threshold=threshold)
        # Step 5: Convert fragment boundaries from indices to time intervals (in seconds)
        for edt in range(len(self.cosine_similarities)):
            print(self.cosine_similarities[edt])
        fragment_boundaries_in_seconds = [self.cosine_similarities[t]['end_time'] for t in fragment_boundaries]

        return fragment_boundaries_in_seconds

    def calculate_the_depth_values(self, cosine_similarities_vals, valleys, valleys_array, peaks):
        # Calculate the depth values based on a formula discussed in a paper
        depth_val = []
        pk_l, pk_r = 0, 1
        for i in range(len(valleys)):
            val = cosine_similarities_vals[valleys[i]]

            if pk_l >= len(peaks) or peaks[pk_l] > valleys[i]:
                left_peak = cosine_similarities_vals[valleys[i]-1]
            else:
                left_peak = cosine_similarities_vals[peaks[pk_l]]
                pk_l += 1

            if pk_r >= len(peaks) or peaks[pk_r] < valleys[i]:
                right_peak = cosine_similarities_vals[valleys[i]+1]
            else:
                right_peak = cosine_similarities_vals[peaks[pk_r]]
                pk_r += 1

            if left_peak == 0 or right_peak == 0:
                print(f'peaks not found: {i} {left_peak} {val} {right_peak}')

            depth = (left_peak - val) + (right_peak - val)
            depth_val.append({'index': valleys_array[i], 'val': depth})

        depth_val = sorted(depth_val, key=lambda x: x['val'], reverse=True)

        return depth_val

    def get_the_fragments(self, depth_val, threshold):
        # Get fragments based on the depth values and threshold
        ctr = 0
        fragment_boundaries = []
        for depth in depth_val:
            if depth['val'] > threshold:
                fragment_boundaries.append(depth['index'])
                ctr += 1
            if self.k_value > 0 and ctr == self.k_value:
                break
        fragment_boundaries = sorted(fragment_boundaries)
        return fragment_boundaries

    def calculate_threshold(self, cosine_similarities_vals, valleys):
        # Calculate the threshold using a formula discussed in the paper
        valleys_scores = np.array([cosine_similarities_vals[i] for i in valleys])
        mean_val_min = np.mean(valleys_scores)
        std_dev_val_min = np.std(valleys_scores)
        threshold = self.m_value * (mean_val_min - std_dev_val_min)

        return threshold

    def calculate_the_valleys_and_peaks(self):
        # Calculate valleys and peaks based on cosine similarities
        cosine_similarities_vals = [score['similarity'] for score in self.cosine_similarities]
        # Step 1: Create a signal from the cosine similarities
        signal = np.arange(0, len(cosine_similarities_vals) * self.step_size, self.step_size)
        # Step 2: Detect valleys and peaks (local minima and maxima) in the signal
        valleys, _ = find_peaks([-score for score in cosine_similarities_vals])
        peaks, _ = find_peaks(cosine_similarities_vals)
        # Step 3: Calculate the depth of each valley and select fragment boundaries
        valleys_array = np.array(valleys)

        return cosine_similarities_vals, signal, valleys, valleys_array, peaks

##### IMPORTANT NOTES #####

### after the whisper gives the transcripts, this transcript will be passed to the "extract_sentences" method
### this transcript should be in a json format
### the json format should be like this: [{"text": "sentence 1", "start": 0, "duration": 1}, {"text": "sentence 2", "start": 1, "duration": 1}, {"text": "sentence 3", "start": 2, "duration": 1}, .....]
### i think the whisper gives the same kind of format but with different keys
### so we need to adjust accordingly

### testing the class
# print("Running.....")

# with open("./testing-the-algo.json", "r", encoding="utf-8") as file:
#     sentences = json.load(file)

# segmenter = Segmentation_algo()
# # segmenter.extract_sentences(sentences)
# # segmenter.calculate_similarities()
# segments = segmenter.segment_the_transcript()
# print(segments)
