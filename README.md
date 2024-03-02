# Welcome to LASER

This file outlines the process for setting up LASER to work locally on your machine.

LASER is divided into two parts: Backend and a Frontend.
You will need to install dependencies for each one seprately, and run each seperately as well.

Another important part is the AI models. You need to put the models in the respective forlders with the given names in this document.


### Backend.

Our backend is written in python.   
It is based on the flask library.  

To install all required dependencies, first install a virtual python environment and activate it. This could be done through Anaconda, Minoconda, Pip etc..
But it should have PIP installed.

Then, run the following command inside the backend folder:

`pip install -r requirements.txt`

But do not run the server yet before placing required models.

### Installing CUDA

To run LASER locally, you should have a PyTorch installation with Cuda runtimes. This requires:
1. A CUDA supported GPU.
2. CUDA supported drivers
3. About 11GB of VRAM minimum.
4. PyTorch version 2.0.0 with cuda 11.7.
    * Other versions might work but it is not tested. Newer versions of PyTorch and Cuda might work.
    We installed it using this command:

    * `conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia
`

#### Running on CPU
in case you cannot install CUDA or do not have a good enough GPU, you could run everything on the CPU.
1. Change all instances of the string 'cuda' in the code to 'cpu'
2. Replace the embedding model for the segmentation task with a default un-quantized version. (Contact us for help, see the end of this document)

## Client (Frontend)

You need to install NodeJS to install the client dependencies.

After installing NodeJS and NPM (node package manager), run the following command inside the client folder:

`npm install`

## AI models

LASER uses multiple custom AI models and some off-the-shelf pre-trained models.

### Transcription

Transcription is done through a custom service that we have created and is running on another machine.  

But to run LASER locally, you must set the use_asr_service flag to False, either in the transcription.py file or in the instantiation of the transcripter in server.py:
`transcriptor = Transcriptor(use_asr_service=False)`

This is because the ASR service can only accessed from a local network. 

If you cannot run ASR along with Summarization models due to a GPU limitation, please contact us and we will give you a link for the ASR service from our lab so you could use it.

### Segmentation

Segmentation needs an embedding model, called flag embedding. 

In our case, we are using an optimized, quantized version of this model to make it faster.
The folder name should be `bge_auto_opt_O4` and it should be directly under the backend folder

Furthermore, you need the BiLSTM trained model. It is called `bilstm_bge_auto_opt_O4_5_best_model.pt` and should be put in the model directory inside the backend.

### Summarization

Summarization needs three models:  

- Full Lecture Summarizer: BART-base
- Long Full Lecture Summarizer: LSG-BART
- Lecture Segment Summarizer + Title Generator: BART-base

The model files are found in the link we submitted and should be put inside the model directory.


### Question Answering

We are using a quantized version of Llama-2 7B. The file name is `llama-2-7b-chat.gguf.q4_K_M`.

The file should be put under the QA_models directory inside the backend directory.



## Running LASER

First, ensure you have gone over the previous steps.

1. Using the virtual environment created for this project and where all dependencies were installed from requirements.txt, run the following command inside the backend folder:
`python server.py`

2. Go to the client folder, and run:
`npm run start`

3. Go to http://localhost:3000
4. Wait for about 30 seconds for some AI models to be setup and loaded.
5. Summarize lectures and learn more efficiently!

## FAQ

Where do I find the models used in LASER so I can run it locally?
We will upload them on Hugging Face spaces soon.


Shield: [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

