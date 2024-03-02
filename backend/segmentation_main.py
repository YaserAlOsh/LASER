from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer, AutoModel
import onnxruntime as rt
import torch

"""
A parent segmentation class that has two children
    - Segmentation_algo
    - Segmentation_model
This class has two methods which are calling the embedding model and
using the embedding model to transform the sentence into a vector representation
"""

# Class definition for the Segmentation_main class.
class Segmentation_main:
    def __init__(self) -> None:
        self.call_the_embedder()

    def call_the_embedder(self):
        # Change the path of the model if needed
        self.tokenizer = AutoTokenizer.from_pretrained('bge_auto_opt_O4')
        self.ort_model = ORTModelForFeatureExtraction.from_pretrained('bge_auto_opt_O4', provider="CUDAExecutionProvider")  # CUDAExecutionProvider
        self.ort_model.to('cuda')


    # Method to embed sentences using the embedding model.
    def embed_sentences(self, text):
        """
        Tokenizes and embeds a sentence using the configured embedding model.

        Parameters:
        - text (str): The input sentence.

        Returns:
        - torch.Tensor: The vector representation of the input sentence.
        """
        # Tokenize sentences
        encoded_input = self.tokenizer(text, padding=True, truncation=True, return_tensors='pt').to('cuda')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.ort_model(**encoded_input)
            # Perform pooling. In this case, cls pooling.
            sentence_embeddings = model_output[0][:, 0]

        # Normalize embeddings
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings[0].cpu()
