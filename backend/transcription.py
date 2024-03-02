#from faster_whisper import WhisperModel
from transformers import pipeline
import torch
import requests

class Transcriptor():
    def __init__(self,use_asr_service=False):
        self.is_setup = False
        self.use_asr_service = use_asr_service
        self.asr_service_url = "http://192.168.10.19:3000/transcribe"
    def set_model(self):
        if self.use_asr_service:
            return
        
        self.pipe = pipeline("automatic-speech-recognition",
                              model="openai/whisper-base.en",
                              torch_dtype=torch.float16, device='cuda')
        self.pipe.model = self.pipe.model.to_bettertransformer()
        self.is_setup = True
    def post_request(self, url, file_path):
        with open(file_path, 'rb') as file:
            files = {'upload_file': file}
            response =  requests.post(url, files=files)
            return response.json()
    def generate_transcript(self, file):
        if self.use_asr_service:
            transcripts =  self.post_request(self.asr_service_url, file)    
            return transcripts['text'] , transcripts['chunks']
        else:
            if not self.is_setup:
                self.set_model()
            transcripts = self.pipe(file,chunk_length_s=30,batch_size=16,return_timestamps=True)
            return transcripts['text'], transcripts['chunks']