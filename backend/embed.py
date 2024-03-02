from fastembed.embedding import FlagEmbedding as Embedding
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch

"""
Methods:
    get_embedding(text)
        - Returns the embedding of the text
    get_embeddings(texts)
        - Returns the embeddings of the texts
    get_top_k(query, embeddings, documents, k=5, thresholds = 0.5)
        - Returns the top k documents that are similar to the query
    get_top_k_from_texts(query, texts, k=5, thresholds=0.5)
        - Returns the top k sentences that are similar to the query
    get_top_k_from_embeddings(query, embeddings, k=5, thresholds=0.5)
        - Returns the top k embeddings that are similar to the query
    get_top_k_from_multi_embeddings(query, embeddings_array, k=5, thresholds=0.5)
        - Returns the top k multi-embeddings that are similar to the query
"""

class Embeddor():
    def __init__(self):
        #self. embedding_model = Embedding(model_name="BAAI/bge-small-en-v1.5", max_length=512)
        self.embedder = SentenceTransformer('msmarco-distilbert-base-tas-b')
    def get_embedding(self,text):
        #embedding = self.embedding_model.query_embed(text) # try both embed and query_embed
        embedding = self.embedder.encode(text)
        #print(embedding)
        return embedding
    def get_embeddings(self,texts):
        embeddings = self.embedder.encode(texts) #list(self.embedding_model.passage_embed(texts))
        return embeddings
    def get_top_k(self,query, embeddings, documents, k=5, thresholds = 0.5):
        # embeddings = [x for x in embeddings if type(x) == np.ndarray and x.shape == (384,)]
        
        #print(embeddings)
        
        # get the query embedding
        query_embedding = list(self. embedding_model .query_embed(query))[0]
        
        # Check and potentially transpose dimensions
        #if query_embedding.shape[0] != 1:
         #   query_embedding = query_embedding.T

        # use numpy to calculate the cosine similarity between the query and the documents
        # scores = np.dot(embeddings, query_embedding)# on second
        scores = np.dot(embeddings, query_embedding)
        # sort the scores in descending order
        sorted_scores = np.argsort(scores)[::-1]
        # filter out scores below the threshold
        sorted_scores = [x for x in sorted_scores if scores[x] > thresholds]
        # return at most k, if there is less than k, return all
        sorted_scores = sorted_scores[:k]
        # return the documents and scores
        return [documents[x] for x in sorted_scores]
    
    def get_top_k_from_texts(self, query, texts, k=5, thresholds=0.5):
        

        corpus_embeddings = self.embedder.encode(texts, convert_to_tensor=True)
        #print(corpus_embeddings[0])
        # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
        top_k = min(k, len(texts))
        #print(query)
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.dot_score(query_embedding, corpus_embeddings)[0]
        #print(cos_scores)
        top_results = torch.topk(cos_scores, k=top_k)

        return top_results[1].cpu().numpy()
        
    def get_top_k_from_embeddings(self, query, embeddings, k=5, thresholds=0.5):
        # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
        top_k = min(k, len(embeddings))
        #print(query)
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.dot_score(query_embedding, embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)

        return top_results[1]
    
    def get_top_k_from_multi_embeddings(self, query, embeddings_array, k=5, thresholds=0.5):
        # flatten the texts array and store an index to keep track of the original text
        embeddings = []
        embeddings_index = []
        for i in range(len(embeddings_array)):
            for E in embeddings_array[i]:
                # CONVERT embedding list to numpy then to cuda
                e = np.array(E)
                embeddings.append(e)
                embeddings_index.append(i)
        # convert embeddings to FloatTensor and store on cuda
        embeddings = torch.FloatTensor(embeddings).to('cuda')
        # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
        top_k = min(k, len(embeddings))
        #print(query)
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.dot_score(query_embedding, embeddings)[0]
        #print(cos_scores)
        top_results = torch.topk(cos_scores, k=top_k)
        
        #print("\n\n======================\n\n")
        #print("Query:", query)
        #print(f"\nTop {k} most similar sentences in corpus:")

        #for score, idx in zip(top_results[0], top_results[1]):
         #   print("(Score: {:.4f} at {})".format(score,embeddings_index[idx]))
        # convert indices to original text index
        top_indices = [embeddings_index[x] for x in top_results[1]]
        # remove duplicates
        top_indices = list(dict.fromkeys(top_indices))
        return top_indices
    
    def get_top_k_from_multi_texts(self, query, texts_array, k=5, thresholds=0.5):
        
        # flatten the texts array and store an index to keep track of the original text
        texts = []
        texts_index = []
        for i in range(len(texts_array)):
            for text in texts_array[i]:
                texts.append(text)
                texts_index.append(i)
        # encode the texts
        corpus_embeddings = self.embedder.encode(texts, convert_to_tensor=True)
        #print(corpus_embeddings[0])
        # Find the closest k sentences of the corpus for each query sentence based on cosine similarity
        top_k = min(k, len(texts))
        #print(query)
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)

        # We use cosine-similarity and torch.topk to find the highest 5 scores
        cos_scores = util.dot_score(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)

        # convert indices to original text index
        top_indices = [texts_index[x] for x in top_results[1]]
        return top_indices[1]