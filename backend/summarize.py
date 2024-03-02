from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoConfig
import os
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
import torch
import re

"""
Methods:
    setup_models()
        - Loads the model from the saved state dict
    count_sentences(s)
        - Returns the number of sentences in the transcript
    compress_ext_sum(transcript, ratio=0.5)
        - Returns the compressed transcript
    summarize(transcript, segment=False)
        - Returns the summary of the full transcript
    summarize_segments(segments)
        - Returns summaries of each segment as well as the titles
"""

class Summarizer():
    def __init__(self):
        print(os.getcwd())  # Print current working directory
        self.is_setup = False  # Flag indicating whether models are set up

    def setup_models(self):
        # Model paths for different summarization scenarios
        self.full_lecture_model_path = "./model/full_lecture_summarizer"  # 1000 tokens
        self.long_lecture_model_path = "./model/full_lecture_summarizer_lsg_2048_v2"
        self.lecture_segment_model_path = "./model/lecture_segment_summarizer_plus_titles_v2"

        # Load tokenizers for different models
        self.full_lecture_tokenizer = AutoTokenizer.from_pretrained(self.full_lecture_model_path)
        self.lecture_segment_tokenizer = AutoTokenizer.from_pretrained(self.lecture_segment_model_path)
        self.long_lecture_tokenizer = AutoTokenizer.from_pretrained(self.long_lecture_model_path)

        # General settings
        self.device = 'cuda'
        self.max_input_length = 1024
        self.max_summary_length = 512
        self.long_input_length = 2048
        self.threshold_long_lecture = 100  # Extra tokens over base model to use long lecture model
        self.batch_size = 4  # Batch size for segments

        # Configuration for model instances
        config = AutoConfig.from_pretrained(self.full_lecture_model_path)
        config.max_length = self.max_summary_length
        config.min_length = 256
        config.no_repeat_ngram_size = 3
        config.early_stopping = True
        config.length_penalty = 2.0
        config.num_beams = 4

        # Load Seq2Seq models for different scenarios
        self.full_lecture_model = AutoModelForSeq2SeqLM.from_pretrained(self.full_lecture_model_path, config=config)
        self.full_lecture_model.to('cuda')

        config = AutoConfig.from_pretrained(self.long_lecture_model_path)
        config.max_length = self.max_summary_length
        config.min_length = 256
        config.no_repeat_ngram_size = 3
        config.early_stopping = True
        config.length_penalty = 2.0
        config.num_beams = 4
        self.long_lecture_model = AutoModelForSeq2SeqLM.from_pretrained(self.long_lecture_model_path, config=config)
        self.long_lecture_model.to('cuda')

        config = AutoConfig.from_pretrained(self.lecture_segment_model_path)
        config.max_length = self.max_summary_length
        config.min_length = 256
        config.no_repeat_ngram_size = 3
        config.early_stopping = True
        config.length_penalty = 2.0
        config.num_beams = 4
        self.lecture_segment_model = AutoModelForSeq2SeqLM.from_pretrained(self.lecture_segment_model_path, config=config)
        self.lecture_segment_model.to('cuda')

        # Initialize TextRank summarizer
        LANGUAGE = 'english'
        stemmer = Stemmer(LANGUAGE)
        self.text_rank_summarizer = TextRankSummarizer(stemmer)
        self.text_rank_summarizer.stop_words = get_stop_words(LANGUAGE)

    def count_sentences(self, s):
        # Count the number of sentences in the transcript
        res = re.split(r'\.|\,|\?|\!', s, 0)
        if len(res[-1].strip()) == 0:
            return len(res) - 1
        return len(res)

    def compress_ext_sum(self, transcript, ratio=0.5):
        # Compress the transcript using TextRank-based summarization
        sns_count = self.count_sentences(transcript)
        sns = min(25, sns_count * ratio)
        parser = PlaintextParser.from_string(transcript, Tokenizer('english'))
        res = []
        for sentence in self.text_rank_summarizer(parser.document, sns):
            res.append(sentence._text)
        return ' '.join(res)

    def summarize(self, transcript, segment=False):
        # Generate a summary for the given transcript
        if not self.is_setup:
            self.setup_models()

        token_count = len(self.full_lecture_tokenizer.encode(transcript))

        if not segment and (token_count - self.max_input_length) > self.threshold_long_lecture:
            # Use the long lecture model for large transcripts
            print("long lecture: ", token_count)
            tokens = self.long_lecture_tokenizer(transcript, return_tensors='pt',
                                                 truncation=True, max_length=self.long_input_length).to(self.device)

            outputs = self.long_lecture_model.generate(**tokens, max_new_tokens=self.max_summary_length)

            output_text = self.long_lecture_tokenizer.decode(outputs[0], skip_special_tokens=True)

        elif not segment:
            # Use the full lecture model for regular transcripts
            tokens = self.full_lecture_tokenizer(transcript, return_tensors='pt',
                                                 truncation=True, max_length=self.max_input_length).to(self.device)

            outputs = self.full_lecture_model.generate(**tokens, max_new_tokens=self.max_summary_length)

            output_text = self.full_lecture_tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            # Segment case
            ratio = token_count / self.max_input_length
            if ratio > 1.1:
                # Compress the transcript for efficient processing
                transcript = self.compress_ext_sum(transcript, ratio=1 / ratio)

            tokens = self.full_lecture_tokenizer(transcript, return_tensors='pt', truncation=True,
                                                 max_length=self.max_input_length)

            outputs = self.full_lecture_model.generate(**tokens, max_new_tokens=self.max_summary_length)

            output_text = self.full_lecture_tokenizer.decode(outputs[0], skip_special_tokens=True)

        return output_text

    def summarize_segments(self, segments):
        # Generate summaries for each segment
        if not self.is_setup:
            self.setup_models()

        for i in range(len(segments)):
            token_count = len(self.full_lecture_tokenizer.encode(segments[i]))
            ratio = token_count / self.max_input_length
            if ratio > 1.1:
                # Compress the segment transcript for efficient processing
                segments[i] = self.compress_ext_sum(segments[i], ratio=1 / ratio)

        res_summaries, res_titles = [], []

        # Create batches of size 2
        for i in range(0, len(segments), self.batch_size):
            # Tokenize the batch
            tokenized = self.lecture_segment_tokenizer(segments[i:i + self.batch_size],
                                                       return_tensors='pt', padding=True,
                                                       truncation=True, max_length=self.max_input_length).to(self.device)
            # Generate the summaries
            with torch.no_grad():
                outputs = self.lecture_segment_model.generate(**tokenized, max_new_tokens=self.max_summary_length)
            output_texts = self.lecture_segment_tokenizer.batch_decode(outputs, skip_special_tokens=True)

            for x in output_texts:
                if len(x.split('\n')) < 2:
                    title = x.split(' ')[0]
                    summary = ' '.join(x.split(' ')[1:])
                else:
                    title = x.split('\n')[0]
                    summary = ' '.join(x.split('\n')[1:])
                res_titles.append(title)
                res_summaries.append(summary)

        return res_titles, res_summaries
