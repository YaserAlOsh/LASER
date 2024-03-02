from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import CTransformers
from embed import Embeddor

"""
Methods:
    chunk_the_transcript(transcript)
        - Split the transcript into chunks of 100 words
        - Returns the chunks of the transcript and the list of sentences
    embed_the_chunks(text_chunks, list_of_sentences, question)
        - Get the top k chunks of the transcript by comparing the question with the chunks
        - Returns the vector store of those k chunks
    create_prompt()
        - Create the prompt for the retrieval model
        - Returns the prompt
    generate_answer(qa_prompt, vector_store, query)
        - Generate the answer to the question
        - Returns the answer
    get_answer(transcript, question)
        - Combines all the functions into one function
        - Returns the answer to the question
"""

class QuestionAnswering:
    def __init__(self):
        # question_answerer = pipeline("question-answering", model='distilbert-base-uncased-distilled-squad')  #model='deepset/roberta-base-squad2')
        self.llm = CTransformers(model="QA_models/llama-2-7b-chat.gguf.q4_K_M.bin",
                                 model_type="llama",
                                 config={'max_new_tokens': 200, 'temperature': 0, 'context_length': 1024, 'gpu_layers': 20})
        self.embedder = Embeddor()

    def chunk_the_transcript(self, transcript):
        """
        Split the transcript into chunks of 100 words.

        Parameters:
        - transcript (str): The input transcript.

        Returns:
        - list: Chunks of the transcript.
        - list: List of sentences.
        """
        # Writing transcript to a file for loading
        with open("user_input.txt", "w", encoding="utf-8") as file:
            file.write(transcript)

        # Loading documents using TextLoader
        loader = TextLoader("user_input.txt")
        documents = loader.load()

        # Splitting documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        text_chunks = text_splitter.split_documents(documents)
        list_of_sentences = [text_chunks[x].page_content for x in range(len(text_chunks))]

        return text_chunks, list_of_sentences

    def embed_the_chunks(self, text_chunks, list_of_sentences, question):
        """
        Get the top k chunks of the transcript by comparing the question with the chunks.

        Parameters:
        - text_chunks (list): Chunks of the transcript.
        - list_of_sentences (list): List of sentences.
        - question (str): The input question.

        Returns:
        - FAISS: Vector store of the top k chunks.
        """
        res = self.embedder.get_top_k_from_texts(question, list_of_sentences)
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/msmarco-distilbert-base-tas-b', model_kwargs={'device': 'cpu'})
        results_sentences = [text_chunks[i] for i in res]
        vector_store = FAISS.from_documents(results_sentences, embeddings)
        vector_store.as_retriever(search_kwargs={'k': 2})

        return vector_store

    def create_prompt(self):
        """
        Create the prompt for the retrieval model.

        Returns:
        - PromptTemplate: Prompt template for the retrieval model.
        """
        template = """
        [INST] <<SYS>>
        Use the following text from a video transcript to answer the user's question as concisely as possible.
        If you don't know the answer, just say you don't know; don't try to make up an answer.
        <</SYS>>
        Context:{context}
        Question:{question}
        Answer:[/INST]
        """

        qa_prompt = PromptTemplate(template=template, input_variables=['context', 'question'])
        return qa_prompt

    def generate_answer(self, qa_prompt, vector_store, query):
        """
        Generate the answer to the question.

        Parameters:
        - qa_prompt (PromptTemplate): Prompt template for the retrieval model.
        - vector_store (FAISS): Vector store of the top k chunks.
        - query (str): The input query.

        Returns:
        - str: The generated answer.
        """
        self.chain = RetrievalQA.from_chain_type(llm=self.llm,
                                                 chain_type='stuff',
                                                 retriever=vector_store.as_retriever(search_kwargs={'k': 2}),
                                                 return_source_documents=True,
                                                 chain_type_kwargs={'prompt': qa_prompt})
        result = self.chain({'query': query})

        return result['result']

    def get_answer(self, transcript, question):
        """
        Combines all the functions into one function.

        Parameters:
        - transcript (str): The input transcript.
        - question (str): The input question.

        Returns:
        - str: The answer to the question.
        """
        chunks, sentences = self.chunk_the_transcript(transcript=transcript)
        vectors = self.embed_the_chunks(text_chunks=chunks, list_of_sentences=sentences, question=question)
        prompt = self.create_prompt()
        answer = self.generate_answer(qa_prompt=prompt, vector_store=vectors, query=question)

        return answer

# Example usage
# transcript = ""
# with open("D:\Junior23\Datasets\MIT Lectures\MIT_courses_chapters\Introduction to Computer Science and Programming in Python_chapters\\video_1\\full_transcript.txt", "r", encoding="utf-8") as file:
#     transcript = file.read()
# question = "What is the programming language that they are using in this lecture?"
# model = QuestionAnswering()
# answer = model.get_answer(transcript=transcript, question=question)
# print(answer)
