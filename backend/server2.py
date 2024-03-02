from flask import Flask, request, jsonify, session, make_response,send_from_directory
from flask_cors import CORS, cross_origin
from grpc import access_token_call_credentials
from pydub import AudioSegment
from embed import Embeddor
from summarize import Summarizer
from transcription import Transcriptor
from models import db, User, UsersLectures, LecturesInfo
from config import ApplicationConfig
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from pytube import YouTube
import numpy as nps
import os
import time
import requests
import argparse
import json
from QuestionAnswering import QuestionAnswering
import faiss
from segmentation_algo import Segmentation_algo
from segmentation_model import SegmentationModel
from youtube_transcript_api import YouTubeTranscriptApi
import base64
from flask_ngrok import run_with_ngrok
import logging
from celery_utils import get_celery_app_instance
from celery import Celery
from flask_socketio import SocketIO, emit


#os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
question_transcript =""

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('flask_cors').level = logging.DEBUG
#app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
#app.config['SESSION_COOKIE_SAMESITE'] = "None"
app = get_celery_app_instance(app)
socketio = SocketIO(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
app.clients = {}

bcrypt = Bcrypt(app)
#CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
# #CORS(app, origins="http://localhost:3000",supports_credentials=True, allow_headers="*", expose_headers="*", send_wildcard=True)
#CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:3000"}},access_token_call_credentials=True, supports_credentials=True)

# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),'uploads')
server_session = Session(app)
db.init_app(app)

with app.app_context():
    db.create_all()
#CORS(app, resources={r"/*": {"origins": ["https://00cd-217-165-164-53.ngrok-free.app"]}}, supports_credentials=True)
#CORS(app, origins=["http://127.0.0.1:3000"],supports_credentials=True)#, allow_headers="*", expose_headers="*")
#run_with_ngrok(app)
CORS(app,resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)
#CORS(app,resources={r"/*": {"origins": ["https://00cd-217-165-164-53.ngrok-free.app"]}}, supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": ["https://00cd-217-165-164-53.ngrok-free.app"],
#                              "CORS_ORIGINS ":["https://00cd-217-165-164-53.ngrok-free.app"]}},
#      origins=["https://00cd-217-165-164-53.ngrok-free.app"],
#      allow_headers=["Content-Type","X-Amz-Date",
#                     "Authorization","X-Api-Key","X-Amz-Security-Token"],
#                     #"Access-Control-Allow-Methods",
#                     #"Access-Control-Allow-Credentials",
#                     #"Access-Control-Allow-Origin",
#                     #"Access-Control-Allow-Headers"],
#       supports_credentials=True)

summarizer = Summarizer()
transcriptor = Transcriptor()
embeddor = Embeddor()
question_answering = QuestionAnswering()
segmentationAlgo = Segmentation_algo()
segmentationModel = SegmentationModel()
#print( "Content-Type: text/turtle")
#print( "Content-Location: mydata.ttl")
#print("Access-Control-Allow-Origin: *")
force_segmentation = False
min_length_segmentation = 10 * 60 # 10 minutes, minimum video length when we automatically do segmentation
min_transcript_chunk_len = 5 # 10 seconds, minimum length of a transcript chunk
min_segment_length = 120 # 2 minutes, minimum length of a segment
# model_size = 'base'
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")


@app.route("/")
def home():
    return {"check": "hello from backend"}

from datetime import datetime

@app.route("/upload", methods=["POST"])
def upload():
    
    user_id = session.get("user_id")

    if not user_id:
        print("id not there ")
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        print("not registered")
        return jsonify({"error": "Unauthorized"}), 401
    
    file = request.files['file']
#     # NOTE: just note that when we will deploy the website we will add the path that we want the file to be saved to in the server's computer 
    file.save(os.path.join(os.getcwd(),'uploads',file.filename))
    file_path = os.path.join(os.getcwd(),'uploads',file.filename)
    print(file_path)
    transcript_text, transcript_chunks = transcriptor.generate_transcript(file_path)
   
    
    # parser = argparse.ArgumentParser()
    # # summarize
    #print(transcripts)
    summary = summarizer.summarize(transcript_text)
    summary_embed = embeddor.get_embedding(summary)

    lecture_summary = UsersLectures(user_id=user.id, upload_date=datetime.now())
    db.session.add(lecture_summary)
    db.session.commit()
    video_info = LecturesInfo(
        id = lecture_summary.id,
        video_url = file.filename,
        video_transcript = transcript_text,
        tags = '',
        summary=summary,summary_vector = summary_embed)  
    db.session.add(video_info)
    db.session.commit()
    return jsonify({"transcript": summary})
    # return jsonify({"FileTranscript" : transcript_text, "FileFirstTimeStamp" : First_timeStamp, "FileChunkTranscript": Chunk_Transcript}) #just a test were i am trying to send back to the frontend the Youtube link

import re
def get_transcript_from_captions(captions):
    srt = captions.generate_srt_captions()
    regex = r'(?:\d+)\s(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\s+(.+?)(?:\n\n|$)'
    offset_seconds = lambda ts: sum(howmany * sec for howmany, sec in zip(map(int, ts.replace(',', ':').split(':')), [60 * 60, 60, 1, 1e-3]))

    transcript = [dict(start = offset_seconds(startTime),
                        end = offset_seconds(endTime),
                        text = ' '.join(ref.split()))\
                            for startTime, endTime, ref in re.findall(regex, srt, re.DOTALL)]
    return transcript
@celery.task
def transcribe_file(file_path):
    transcript_text, transcript_chunks = transcriptor.generate_transcript(file_path)
    return transcript_text, transcript_chunks

@app.route("/youtubeUpload", methods=['POST'])
def youtubeUpload():

    user_id = session.get("user_id")

    if not user_id:
        print("id not there ")
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        print("not registered")
        return jsonify({"error": "Unauthorized"}), 401


    data = request.get_json(); #reciving data from frontend in json format
    yt = YouTube(data["link"]) #getting the link from the json data 
    video = yt.streams.filter(only_audio=True).first() #downloading the video from the link
    out_file = video.download(output_path = 'uploads\\' )
    base, ext = os.path.splitext(out_file)
    new_file = base + '.wav'
    if not os.path.exists(new_file):
        os.rename(out_file, new_file)


    # downloading youtube thumbnail
    try:
       thumbnail_url = yt.thumbnail_url
       response = requests.get(thumbnail_url)
       thumbnail_data = response.content
       date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
       thumbnail_fileName = os.path.join("E:\\Senior\\LASER-main\\backend\\uploads\\Accounts_images\\",f'thumbnail_{date}.jpg')
       thumbnail_image_name = f'thumbnail_{date}.jpg'
       with open(thumbnail_fileName, 'wb') as thumbnail_file:
            thumbnail_file.write(thumbnail_data)
       
      

       print("Thumbnail downloaded successfully")

    except Exception as e:
        print(f'Error: {str(e)}')

 


    # ..............................
    files = new_file
    #print(files)
    #print()
    #print(type(data)) #for testing purposes you can remove it
    #print()
    #print(data["link"]) # same here (only for testing purposes
    ## Get Transcript from youTube
    
    video_length = yt.length # in seconds
    First_timeStamp = []
    Chunk_Transcript = []
    transcript_chunks = []
    if False and 'en' in yt.captions:
        en_cap = yt.captions['en']
   
        #transcript = get_transcript_from_captions(en_cap)
        transcript  = YouTubeTranscriptApi.get_transcript(yt.video_id,languages=['en'])
        
        transcript_text = ' '.join([x['text'] for x in transcript])
        transcript_chunks = [{'start':x['start'],'end':x['start']+x['duration'],'text':x['text']} for x in transcript]
        
        #print(transcript_text)
    else:
       
        ## this is server2.py which we tried to use celery in.
        transcript_text, transcript_chunks = generate_transcript.delay(new_file)
        # global question_transcript 
        user_id = session.get("user_id")
        
 
        print(user_id)
        print("hello ")
        # print(transcript_from_DB)
        print()
        print("hello ")
        question_transcript = transcript_text
        # print(question_transcript)
        #print(transcript_chunks)
        for i in range(len(transcript_chunks)):
            f,s = transcript_chunks[i]["timestamp"]
            transcript_chunks[i]['start'] = f
            transcript_chunks[i]['end'] = s
            if s == None:
                transcript_chunks[i]['end'] = video_length
            #First_timeStamp.append(f)
            #Chunk_Transcript.append(transcript_chunks[i]["text"])
    #print(transcript_chunks)
    st=0
    chunk_duration=0
    for i in range(len(transcript_chunks)):
        chunk_duration += transcript_chunks[i]['end'] - transcript_chunks[i]['start']
        if chunk_duration >= min_transcript_chunk_len:
            First_timeStamp.append(transcript_chunks[st]['start'])
            Chunk_Transcript.append(' '.join([x['text'] for x in transcript_chunks[st:i+1]]))
            chunk_duration = 0
            st=i+1
    # get video length

    
    lecture_summary = UsersLectures(user_id=user.id, upload_date=datetime.now())
    db.session.add(lecture_summary)
    db.session.commit()
    # convert segments time into one str
    segments_str = ''
    
    print("video length: ", video_length)
    print("done with the transcript")
   
    video_info = LecturesInfo(
        id = lecture_summary.id,
        summary = [],
        lecture_name = base,
        video_url = data["link"],
        video_transcript = transcript_text,
        tags = '',
        summary_vector = [],
        segments="",
        thumbnail_image = thumbnail_image_name )  
    db.session.add(video_info)
    db.session.commit() 
    app.clients[user_id] = {'last_transcript_chunks': transcript_chunks, "last_video_length": video_length,"last_transcript_text":transcript_text}
   

    return jsonify({"Youtubetranscript" : transcript_text, "First_timeStamp" : First_timeStamp, "Chunk_Transcript": Chunk_Transcript,"Video_length":video_length}) #just a test were i am trying to send back to the frontend the Youtube link



def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response
def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/register",methods=['POST'])
def register_user():
     #if request.method == "OPTIONS": # CORS preflight
       # return _build_cors_preflight_response()
     #elif request.method == "POST": # The actual request following the preflight

    email = request.json["email"]
    password = request.json["password"]
    username = request.json["username"] 

    #print(email)
    user_exists = User.query.filter_by(email=email).first() is not None
    #print(user_exists)
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)  
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.id
    #print(session)
    res= jsonify({
        "id": new_user.id,
        "username": new_user.username,  # Add this line for username
        "email": new_user.email
    })
    return res
      #  return _corsify_actual_response(res)
     #else:
      #  raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))



# headers = {'Content-Type': 'application/json'}

# response = requests.post(headers=headers)

@app.route("/login", methods=['POST'])
def login_user():
    
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email
    })


@app.route("/logout", methods=["POST"])
@cross_origin()
def logout_user():
    session.pop("user_id")
    return "200"


@app.route("/account/me",methods=["POST","GET"])
#@cross_origins(origin=["https://00cd-217-165-164-53.ngrok-free.app"], supports_credentials=True)
def get_current_user():
    user_id = session.get("user_id")
    print("get current user")
    print(user_id)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    print("#### @me ####")
    print(user_id)
    user = User.query.filter_by(id=user_id).first()
    #response.headers['Access-Control-Allow-Origin'] = 'https://00cd-217-165-164-53.ngrok-free.app'
    #response.headers.add("Access-Control-Allow-Origin",  'https://00cd-217-165-164-53.ngrok-free.app')
    return jsonify({
        "username": user.username,  # Modify this line to include the username
        "email": user.email
    })


@app.route("/mylectures",methods=["POST"])
def get_my_lectures():
    user_id = session.get("user_id")
    #user_lectures =  UsersLectures.query.filter_by(user_id=user_id).all()
    #lecture_ids = [x.id for x in user_lectures]
    #print(lecture_ids)
    print("#### @mylectures ####")
    print(user_id)

    #lectures = LecturesInfo.query.filter(LecturesInfo.id.in_(lecture_ids)).all()
    #user_lectures =  UsersLectures.query.filter_by(user_id=user_id).join(LecturesInfo, LecturesInfo.id==UsersLectures.id).all()
    # join user lectures with lectures info
    user_lectures = db.session.query(
         UsersLectures, LecturesInfo,
    ).filter(UsersLectures.user_id == user_id).filter(UsersLectures.id == LecturesInfo.id).all()
    #print(user_lectures)
    #for x,l in user_lectures:
     #   print(x)
      #  print(l)

    lectures = [
        {"id": l.id,
        "video_url": x.video_url,
        "video_transcript": x.video_transcript,
        "date":l.upload_date,
        "summary": x.summary,
        "thumbnail_image":x.thumbnail_image} 
                for l,x in user_lectures]
    for l,x in user_lectures:
        print(x.thumbnail_image)
    #print("### ACTUAL LECTURES INFO ###")
    #print(lectures)
    return jsonify({"lectures": lectures})


@app.route("/mylectures/search",methods=["POST"])
def search_lectures():
    
    data = request.get_json()
    query = data.get('searchQuery')
    user_id = session.get("user_id")
    print(query)
    # conver the query to vector
    #query_vector = embeddor.get_embedding(querys) 
    #query_vector = np.array([query_vector.astype('float32')])  # Add an extra dimension

    #..........................................
    # get user summaries from db
    lecture_ids = [x.id for x in UsersLectures.query.filter_by(user_id=user_id).all()]
    # get summaries from db
    lectures = LecturesInfo.query.filter(LecturesInfo.id.in_(lecture_ids)).all()
    # top_res = {}
    if len(lectures) > 0:
        #vectors = [np.array(x.summary_vector) for x in lectures]
        # some videos have null vectors thats the problem
        
        #top_res = embeddor.get_top_k(querys, vectors, lectures)
        summaries_vectors = [x.summary_vector for x in lectures]
        #top_res = embeddor.get_top_k_text(querys, summaries, lectures)
        #vectors = embeddor.get_embeddings(summaries)
        #res = embeddor.get_top_k_from_texts(query, summaries)
        res = embeddor.get_top_k_from_multi_embeddings(query, summaries_vectors)
    """ vectors = np.array(vectors)
    
    vector_length = vectors.shape[1]
    index = faiss.IndexFlatL2(vector_length)

    # Add items to the index
    index.add(vectors.astype('float32'))

    # Find the nearest neighbor
    distances, indices = index.search(query_vector.astype('float32'), 4) """
    # indices = indices.flatten().tolist()

    #print()
    #print(type(indices))
    #print()
    top_res = [lectures[i] for i in res]
    #top_res = lectures[indices[0][0]]
    #print("start")
    #print(type(top_res))
    #print(top_res)
    #print()
    #print()
    #print("end")
    lectures = [
        {"id": x.id,
        "video_url": x.video_url,
        "video_transcript": x.video_transcript,
        "date": "", #l.upload_date,
        "summary": x.summary,
        "thumbnail_image":x.thumbnail_image} 
                for x in top_res]
    
    
    return jsonify({"documents":lectures})

@app.route("/answer_question",methods=["POST"])
def answering_questions():
    data = request.get_json()
    query = data.get('question')
    print('user id :')
    user_id = session.get("user_id")
    
    
    user = User.query.filter_by(id=user_id).first().id
    print(user)
    print('user id :')
    query_res = db.session.query(
         UsersLectures, LecturesInfo,
    ).order_by(UsersLectures.upload_date.desc()).filter(UsersLectures.user_id == user_id).filter(UsersLectures.id == LecturesInfo.id).first()#.order_by(UsersLectures.upload_date).first()
   
    # transcript_id = query_res.order_by(UsersLectures.upload_date.desc()).first().id
    # transcript_from_DB = LecturesInfo.query.filter_by(id = transcript_id).first().video_transcript

    print("Sending answer")

    predicted_answer = question_answering.get_answer(transcript=query_res[1].video_transcript, question=query)
    print("Answer received")

    return jsonify({"answer": predicted_answer})


@app.route("/uploads/Accounts_images/<path:filename>")
def uploaded_image(filename):
    return send_from_directory("uploads/Accounts_images",filename)

@app.route("/Summary", methods=["POST"])
def summarize():
    data = request.get_json()
    user_id = session.get("user_id")
    video_length = app.clients[user_id]["last_video_length"]
    transcript_chunks = app.clients[user_id]["last_transcript_chunks"]
    transcript_text = app.clients[user_id]["last_transcript_text"]
    #print(transcript_text)
    #print(type(transcript_chunks[0]))
    #print(transcript_chunks[0])
    print(transcript_chunks)
    summaries = []
    summaries_embeds = []
    segments = [] # replaced with None
    print("starting with the segmentation")
    if video_length >= min_length_segmentation or force_segmentation: # if the video is longer than 10 minutes, or if the user forced segmentations.
        #### Segmentation
        #print("Helloooos")
        segment_method = data['quality']
        segment_method = 'fast'
        #print("received the segment method")
        start_time = time.time()
        if segment_method == 'high':
            #print("it will segment using the segmentation model")
            segments = segmentationModel.segment_the_transcript(transcript_chunks)
            #print("returned the resutl of the segmentation model")
            #print(segments)
        else:
            #print("it will segment using the segmentation algorithm")
            segments = segmentationAlgo.segment_the_transcript(transcript_chunks)
            #print("returned the resutls of the segmentation algorithm")
            #print(segments) 
        end_time = time.time()
        print("segmentation time: ", end_time-start_time)
        print(segments)
        segments=sorted(segments)
        # get the transcripts part of each segment
        transcripts = []
        s=0
        for b in segments:
            print("s: ", s)
            for i in range(s,len(transcript_chunks)):
                if transcript_chunks[i]['end'] == b:
                    e = i
                    break
            transcripts.append(' '.join([x['text'] for x in transcript_chunks[s:e+1]]))
            s = i+1
        # check if the last segment boundary is not the end of the video
        rem_time =  video_length - segments[-1]
        if rem_time > min_transcript_chunk_len:
            if rem_time > min_segment_length:
                segments.append(video_length)
                transcripts.append(' '.join([x['text'] for x in transcript_chunks[s:]]))
            else:
                print('last segment is not the end of the video: ',transcript_chunks[-1]['end'] - segments[-1])
                transcripts[-1] = transcripts[-1] + ' '+ ' '.join([x['text'] for x in transcript_chunks[s:]])
        #print(transcripts)
        print("====================================")
        #for t in transcripts:
            #print(t)
         #   print("==============================================")
          #  summary = summarizer.summarize(t,segment=True)
           # summary_embed = embeddor.get_embedding(summary)
            #summaries_embeds.append(summary_embed.tolist())
            #summaries.append(summary)
        summaries = summarizer.summarize_segments(transcripts)
        summaries_embeds =  [x.tolist() for x in embeddor.get_embeddings(summaries)] 
        print("====================================")
    else:
        summary = summarizer.summarize(transcript_text)
        summary_embed = embeddor.get_embedding(summary)
        summaries.append(summary)
        summaries_embeds.append(summary_embed.tolist())

    if segments is not None:
        segments_str = ','.join([str(x) for x in segments]) ## We can add titles of segments here later.

    return jsonify({"summaries":summaries,"segments":segments_str})




if __name__ == '__main__':
    app.run(debug=True, port=5000)
    #app.run() # ngrok test