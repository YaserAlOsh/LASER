# !pip install langchain
#!pip install sentence-transformers
#!pip install faiss-gpu

import os
# from langchain import PromptTemplate
# from langchain.chains import RetrievalQA
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.document_loaders import PyPDFLoader, DirectoryLoader
# from langchain.document_loaders import TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.llms import CTransformers
import sys
import datetime
# os.chdir("E:\")
from embed import Embeddor
# import time as t

# with open("D:\Junior23\Datasets\MIT Lectures\MIT_courses_chapters\Introduction to Computer Science and Programming in Python_chapters\\video_1\\transcript_1_1.txt", "r", encoding="utf-8") as file:
#     transcript = file.read()

# user_input = transcript #input("Enter your text: ")

# with open("user_input.txt", "w", encoding="utf-8") as file:
#     file.write(user_input)


# loader = TextLoader("user_input.txt")
# documents=loader.load()

# text_splitter=RecursiveCharacterTextSplitter(
#                                              chunk_size=1000,
#                                              chunk_overlap=20)
# text_chunks=text_splitter.split_documents(documents)

# # text_chunks=text_splitter.split_documents(documents)

# # print(len(text_chunks))

# embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device':'cpu'})


# #Step 4: Convert the Text Chunks into Embeddings and Create a FAISS Vector Store
# vector_store=FAISS.from_documents(text_chunks, embeddings)

# vector_store.as_retriever(search_kwargs={'k': 2})

# # !pip install ctransformers

# print(os.getcwd())
# llm=CTransformers(model="llama2/llama-2-7b-chat.ggmlv3.q4_0.bin",
#                   model_type="llama",
#                   config={'max_new_tokens': 2000, 'temperature':0.1,'context_length':2048})
# print("model downloaded")
# template="""Use the following pieces of information to answer the user's question.
# If you don't know the answer just say you don't know, don't try to make up an answer.

# Context:{context}
# Question:{question}

# Only return the helpful answer below and nothing else
# Helpful answer
# """

# qa_prompt=PromptTemplate(template=template, input_variables=['context', 'question'])



# chain = RetrievalQA.from_chain_type(llm=llm,
#                                    chain_type='stuff',
#                                    retriever=vector_store.as_retriever(search_kwargs={'k': 2}),
#                                    return_source_documents=True,
#                                    chain_type_kwargs={'prompt': qa_prompt})

# question="what type of programming language is used in this course?"
# result=chain({'query':question})
# print(result['result'])

#################################################################################################################################
print("Running...")
with open("D:\Junior23\Datasets\MIT Lectures\MIT_courses_chapters\Introduction to Computer Science and Programming in Python_chapters\\video_1\\full_transcript.txt", "r", encoding="utf-8") as file:
    transcript = file.read()

# user_input = transcript #input("Enter your text: ")

# with open("user_input.txt", "w", encoding="utf-8") as file:
#     file.write(user_input)


# loader = TextLoader("user_input.txt")
# documents=loader.load()

# text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,
#                                              chunk_overlap=20)
# text_chunks=text_splitter.split_documents(documents)

# list_of_sentences = [text_chunks[x].page_content for x in range(len(text_chunks))]

# question="Which algorithm did the lecturer mention for finding the square root of a number? Explain it in details."

# embedder = Embeddor()
# res, vector_embedding = embedder.get_top_k_from_texts(question, list_of_sentences)
# # print([text_chunks[i] for i in res])

# embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/msmarco-distilbert-base-tas-b', model_kwargs={'device':'cpu'})

# results_sentences = [text_chunks[i] for i in res]
# print(results_sentences)
# vector_store=FAISS.from_documents(results_sentences, embeddings)

# vector_store.as_retriever(search_kwargs={'k': 2})

# llm=CTransformers(model="QA_models/llama-2-7b-chat.gguf.q4_K_M.bin",
#                   model_type="llama",
#                   config={'max_new_tokens': 100, 'temperature':0,'context_length':512,'gpu_layers':10})
# print("model downloaded")

# # question="what type of programming language is used in this course?"
# # template = f"""Use the following pieces of information to answer the user's question.
# #     If you don't know the answer just say you don't know, don't try to make up an answer.
# #     Only return the helpful answer below and nothing else
# #     Helpful answer
# #     Context:
# #     """
# # for i in range(len(results_sentences)):
# #     template+=f"""
# #     {results_sentences[i].page_content}
# #     """
# # template += f"Question:{question}"
# # print(template)
# # print(llm(template))
# # template="""Use the following pieces of information to answer the user's question.
# # If you don't know the answer just say you don't know, don't try to make up an answer.

# # Context:{context}
# # Question:{question}

# # Only return the helpful answer below and nothing else
# # Helpful answer
# # """

# template="""
# [INST] <<SYS>>
# Use the following pieces of information to answer the user's question. If you don't know the answer just say you don't know, don't try to make up an answer.
# <</SYS>>
# Context:{context}
# Question:{question}[/INST]
# Only return the helpful answer below and nothing else
# Helpful answer
# """
# # print(llm(template))

# qa_prompt=PromptTemplate(template=template, input_variables=['context', 'question'])

# chain = RetrievalQA.from_chain_type(llm=llm,
#                                    chain_type='stuff',
#                                    retriever=vector_store.as_retriever(search_kwargs={'k': 2}),
#                                    return_source_documents=True,
#                                    chain_type_kwargs={'prompt': qa_prompt})

# result=chain({'query':question})
# print(result['result'])

from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch
model_name_or_path = "TheBloke/Yi-6B-AWQ" #"TheBloke/openinstruct-mistral-7B-AWQ"
from awq import AutoAWQForCausalLM

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path,trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name_or_path,
#     low_cpu_mem_usage=True,
#     # load in 16 bit
#     torch_dtype=torch.float16,
#     # load_in_8bit=True,
#     device_map="cuda:0"
# )
model = AutoAWQForCausalLM.from_quantized(model_name_or_path,low_cpu_mem_usage=True, fuse_layers=False,trust_remote_code=True)

# Using the text streamer to stream output one token at a time
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

prompt = "Tell me about AI"
import time
st = time.time()
question="Which algorithm did the lecturer mention for finding the square root of a number? Explain it in short."
import json
embedder = Embeddor()
with open("D:\Junior23\Datasets\MIT Lectures\MIT_courses_chapters\Introduction to Computer Science and Programming in Python_chapters\\video_1\\video_1.json",'r') as f:
    transcript = json.load(f)
# group windows of 10
text_chunks = [' '.join([t['text'] for t in transcript[i:i+10]]) for i in range(0, len(transcript), 10)]
res = embedder.get_top_k_from_texts(question, text_chunks)
context = '\n'.join([text_chunks[i] for i in res])
# # print([text_chunks[i] for i in res])
prompt_template=f'''Use the following text from a lecture transcript to answer the user's question. If you don't know the answer just say you don't know.
Stop after answering.
### Instruction:
Context:{context}
Question:{question}

Answer:
'''

# prompt_template=f'''<|im_start|>system
# Lecture Assistent<|im_end|>
# <|im_start|>user
# {prompt_template}<|im_end|>
# <|im_start|>assistant'''
# Convert prompt to tokens
tokens = tokenizer(
    prompt_template,
    return_tensors='pt'
).input_ids.cuda()

generation_params = {
    "do_sample": True,
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_new_tokens": 512,
    "repetition_penalty": 1.1
}

# Generate streamed output, visible one token at a time
#generation_output = model.generate(
#    tokens,
#    streamer=streamer,
#    **generation_params
#)

# Generation without a streamer, which will include the prompt in the output
generation_output = model.generate(
    tokens,
    **generation_params
)

# Get the tokens from the output, decode them, print them
token_output = generation_output[0]
#text_output = tokenizer.decode(token_output)
print(tokens.shape[1])
text_output = tokenizer.decode(token_output[tokens.shape[1]:],skip_special_tokens=True)
print('Time taken: ', time.time()-st)
print("model.generate output: ", text_output)