from flask import Flask, request, jsonify, session, make_response,send_from_directory,send_file
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
# import toPDF 
from reportlab.pdfgen import canvas
from io import BytesIO
from fpdf import FPDF



question_transcript =""

app = Flask(__name__)
app.config.from_object(ApplicationConfig)


app.clients = {}

bcrypt = Bcrypt(app)
client_server =  ["http://localhost:3000","https://985srg9d-3000.inc1.devtunnels.ms/"]
CORS(app, resources={r"/*": {"origins": client_server}}, supports_credentials=True)
#CORS(app, origins=frontend_link,supports_credentials=True, allow_headers="*", expose_headers="*", send_wildcard=True)
#CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:3000"}},access_token_call_credentials=True, supports_credentials=True)

# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),'uploads')
server_session = Session(app)
db.init_app(app)

with app.app_context():
    db.create_all()




client_server = "http://127.0.0.1:5000"

summarizer = Summarizer()
transcriptor = Transcriptor()
embeddor = Embeddor()
question_answering = QuestionAnswering()
segmentationAlgo = Segmentation_algo()
segmentationModel = SegmentationModel()

force_segmentation = False
min_length_segmentation = 60 * 10 # 10 minutes, minimum video length when we automatically do segmentation
min_transcript_chunk_len = 5 # 10 seconds, minimum length of a transcript chunk
min_segment_length = 120 # 2 minutes, minimum length of a segment



@app.route("/")
def home():
    return {"check": "hello from backend"}

from datetime import datetime
# Define a route for handling file uploads via POST request

@app.route("/upload", methods=["POST"])
def upload():
    
    user_id = session.get("user_id")
    # Check if the user is not authorized (no user ID)

    if not user_id:
        print("id not there ")
        return jsonify({"error": "Unauthorized"}), 401
    # Query the user from the database based on the user ID

    user = User.query.filter_by(id=user_id).first()
    # Check if the user is not registered

    if user is None:
        print("not registered")
        return jsonify({"error": "Unauthorized"}), 401
    # Get the uploaded file from the request

    file = request.files['file']
    # Save the file to the 'uploads' directory
    file.save(os.path.join(os.getcwd(),'uploads',file.filename))
    # Create file path and name
    file_path = os.path.join(os.getcwd(),'uploads',file.filename)
    file_name = file_path if len(file_path.split('.')) < 2 else file_path.split('.')[0]
    # get video length from the file
    video = AudioSegment.from_file(file_path)
    video.export(file_name + '.mp3', format="mp3")
    video_length = video.duration_seconds
    

    First_timeStamp = []
    Chunk_Transcript = []
    transcript_chunks = []
    # Extract transcript information using the transcriptor

    transcript_text, transcript_chunks = transcriptor.generate_transcript(file_name + '.mp3')
    
    user_id = session.get("user_id")
    # Process and format transcript chunks
    for i in range(len(transcript_chunks)):
        f,s = transcript_chunks[i]["timestamp"]
        transcript_chunks[i]['start'] = f
        transcript_chunks[i]['end'] = s
        if s == None:
            transcript_chunks[i]['end'] = video_length


    st=0
    chunk_duration=0
    # Process and format transcript chunks
    for i in range(len(transcript_chunks)):
        chunk_duration += transcript_chunks[i]['end'] - transcript_chunks[i]['start']
        if chunk_duration >= min_transcript_chunk_len:
            First_timeStamp.append(transcript_chunks[st]['start'])
            Chunk_Transcript.append(' '.join([x['text'] for x in transcript_chunks[st:i+1]]))
            chunk_duration = 0
            st=i+1


    # Create a database entry for the lecture 

    lecture_summary = UsersLectures(user_id=user.id, upload_date=datetime.now())
    db.session.add(lecture_summary)
    db.session.commit()
    # convert segments time into one str
    segments_str = ''
    
   
    video_info = LecturesInfo(
        id = lecture_summary.id,
        summary = [],
        lecture_name = file_name,
        video_url = file_path,
        video_transcript = transcript_text,
        tags = '',
        summary_vector = [],
        segments="",
        thumbnail_image = "no image unfortunately" )  
    db.session.add(video_info)
    db.session.commit() 
    app.clients[user_id] = {'last_video_id': lecture_summary.id,
                            'last_transcript_chunks': transcript_chunks,
                             "last_video_length": video_length,
                             "last_transcript_text":transcript_text}


    return jsonify({"Youtubetranscript" : transcript_text, "First_timeStamp" : First_timeStamp, "Chunk_Transcript": Chunk_Transcript,"Video_length":video_length})
import re
# this is to recive data from the frontend and then resend the data back to the frontend in order to print the youtube generated transcript
@app.route("/youtubeUpload", methods=['POST'])
@cross_origin(supports_credentials=True,expose_headers=["X-ACCESS_TOKEN"])
 
def youtubeUpload():
    # Get the user ID from the session

    user_id = session.get("user_id")
    # Get JSON data from the frontend

    data = request.get_json();
    if not user_id:
        print("id not there ")
        return jsonify({"error": "Unauthorized"}), 401
    # Query the user from the database based on the user ID

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        print("not registered")
        return jsonify({"error": "Unauthorized"}), 401

    # Download the YouTube video from the provided link
    yt = YouTube(data["link"]) #getting the link from the json data 
    video = yt.streams.filter(only_audio=True).first() #downloading the video from the link
    out_file = video.download(output_path = 'uploads\\' )
    base, ext = os.path.splitext(out_file)
    new_file = base + '.wav'
    # Rename the downloaded file to '.wav'

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
    ## Get Transcript from youTube
    
    video_length = yt.length # in seconds
    First_timeStamp = []
    Chunk_Transcript = []
    transcript_chunks = []
    print(yt.captions)
    has_en_lang=False
    # for k in yt.captions:
    #     print(k)
    #     if 'english' in yt.captions[k].lang.lower():
    #         has_en_lang=True
    #         break
    # Get transcript from YouTube

    transcript_list = YouTubeTranscriptApi.list_transcripts(yt.video_id)
    #print(transcript_list)
    #if 'en' in yt.captions:
    try:
        #en_cap = yt.captions['en']
        transcript = transcript_list.find_manually_created_transcript(['en'])
        if transcript == None:
            transcript_list.find_manually_created_transcript()
            # translate
            transcript = transcript.translate('en')
        print("load transcript from youtube captions")
        transcript  = transcript.fetch() #YouTubeTranscriptApi.get_transcript(yt.video_id,languages=['en'])
        
        transcript_text = ' '.join([x['text'] for x in transcript])
        transcript_chunks = [{'start':x['start'],'end':x['start']+x['duration'],'text':x['text']} for x in transcript]
        
        #print(transcript_text)
    except:
        # If no transcript is found, use the transcriptor to generate one
        transcript_text, transcript_chunks = transcriptor.generate_transcript(new_file)

        for i in range(len(transcript_chunks)):
            f,s = transcript_chunks[i]["timestamp"]
            transcript_chunks[i]['start'] = f
            transcript_chunks[i]['end'] = s
            if s == None:
                transcript_chunks[i]['end'] = video_length
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
   
    video_info = LecturesInfo(
        id = lecture_summary.id,
        summary = [],
        lecture_name = base.split('\\')[-1],
        video_url = data["link"],
        video_transcript = transcript_text,
        tags = '',
        summary_vector = [],
        segments="",
        thumbnail_image = thumbnail_image_name )  
    db.session.add(video_info)
    db.session.commit() 
    # Update client information for the user
    app.clients[user_id] = {'last_video_id': lecture_summary.id,
                            'last_transcript_chunks': transcript_chunks,
                             "last_video_length": video_length,
                             "last_transcript_text":transcript_text}


    return jsonify({"Youtubetranscript" : transcript_text, "First_timeStamp" : First_timeStamp, "Chunk_Transcript": Chunk_Transcript,"Video_length":video_length}) 

@app.route("/register",methods=['POST'])
def register_user():
     #if request.method == "OPTIONS": # CORS preflight
       # return _build_cors_preflight_response()
     #elif request.method == "POST": # The actual request following the preflight
    # Extract user information from the JSON request
    email = request.json["email"]
    password = request.json["password"]
    username = request.json["username"] 

    #print(email)
    # Check if the user already exists in the database
    user_exists = User.query.filter_by(email=email).first() is not None
    #print(user_exists)
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    # Hash the user's password before storing it
    hashed_password = bcrypt.generate_password_hash(password)
    # Create a new user in the database
    new_user = User(username=username, email=email, password=hashed_password)  
    db.session.add(new_user)
    db.session.commit()
    # Set the user_id in the session for the newly registered user
    session["user_id"] = new_user.id
    # Create a JSON response with user information
    res= jsonify({
        "id": new_user.id,
        "username": new_user.username,  # Add this line for username
        "email": new_user.email
    })
    return res
"""
login_user: Handle user login via POST request
"""
@app.route("/login", methods=['POST'])
@cross_origin(supports_credentials=True,expose_headers=["X-ACCESS_TOKEN"])
def login_user():
    # Extract user credentials from the JSON request
    email = request.json["email"]
    password = request.json["password"]
# Query the database to find the user with the provided email
    user = User.query.filter_by(email=email).first()
    # Check if the user does not exist
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    # Check if the provided password matches the hashed password in the database

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    # Set the user_id in the session for the logged-in user

    session["user_id"] = user.id
    # Create a JSON response with user information
    return jsonify({
        "id": user.id,
        "email": user.email
    })
"""
logout_user: Handle user logout via POST request
"""
@app.route("/logout", methods=["POST"])

def logout_user():
    # Remove the user_id from the session to log out the user
    session.pop("user_id")
    # Create a JSON response with an empty user ID indicating successful logout
    return jsonify({
        "id": ""
    })
"""
logout_user: Handle user logout via POST request
"""
@app.route("/account",methods=["GET"])
def get_current_user():
    # Check if the user is not authorized (no user ID)
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    # Query the user from the database based on the user ID
    user = User.query.filter_by(id=user_id).first()
    # Check if the user is not registered
    return jsonify({
        "username": user.username,  # Modify this line to include the username
        "email": user.email
    })

"""
get_my_lectures: Handle getting the user's lectures via POST request
"""
@app.route("/mylectures",methods=["POST"])
def get_my_lectures():
    # Check if the user is not authorized (no user ID)
    user_id = session.get("user_id")
    # join user lectures with lectures info
    user_lectures = db.session.query(
         UsersLectures, LecturesInfo,
    ).filter(UsersLectures.user_id == user_id).filter(UsersLectures.id == LecturesInfo.id).all()
    # get summaries from db
    lectures = [
        {"id": l.id,
        "video_url": x.video_url,
        "video_name":x.lecture_name,
        "video_transcript": x.video_transcript,
        "date":l.upload_date,
        "summary": x.summary,
        "thumbnail_image":x.thumbnail_image} 
                for l,x in user_lectures]
    # Create a JSON response with the user's lectures
    return jsonify({"lectures": lectures})
"""
search_lectures: Handle searching the user's lectures via POST request
"""
@app.route("/mylectures/search",methods=["POST"])
def search_lectures():
    # get the search query from the request
    data = request.get_json()
    query = data.get('searchQuery')
    user_id = session.get("user_id")
    
    # get user summaries from db
    lecture_ids = [x.id for x in UsersLectures.query.filter_by(user_id=user_id).all()]
    # get summaries from db
    lectures = LecturesInfo.query.filter(LecturesInfo.id.in_(lecture_ids)).all()
    user_lectures = db.session.query(
         UsersLectures, LecturesInfo,
    ).filter(UsersLectures.user_id == user_id).filter(UsersLectures.id == LecturesInfo.id).all()

    lectures = [x[1] for x in user_lectures]
    # if there are summaries
    if len(lectures) > 0:
        # get the embeddings of the summaries
        summaries_vectors = [x.summary_vector for x in lectures]
        # get the indices of the top k most similar summaries to the query
        res = embeddor.get_top_k_from_multi_embeddings(query, summaries_vectors)
    else:
        return jsonify({"documents":[]})
    # get the top k most similar summaries
    top_res = [(user_lectures[i][0], lectures[i]) for i in res]
    # format the summaries
    lectures = [
        {"id": x.id,
        "video_url": x.video_url,
        "video_name":x.lecture_name,
        "video_transcript": x.video_transcript,
        "date": l.upload_date,
        "summary": x.summary,
        "thumbnail_image":x.thumbnail_image} 
                for l,x in top_res]
    # Create a JSON response with the user's lectures
    return jsonify({"documents":lectures})
"""
answer_question: Handle answering a question via POST request
"""
@app.route("/answer_question",methods=["POST"])
def answering_questions():
    # get the question from the request
    data = request.get_json()
    query = data.get('question')
    user_id = session.get("user_id")
    
    # get user summaries from db
    user = User.query.filter_by(id=user_id).first().id
    # get summaries from db
    query_res = db.session.query(
         UsersLectures, LecturesInfo,
    ).order_by(UsersLectures.upload_date.desc()).filter(UsersLectures.user_id == user_id).filter(UsersLectures.id == LecturesInfo.id).first()#.order_by(UsersLectures.upload_date).first()
   
    # transcript_id = query_res.order_by(UsersLectures.upload_date.desc()).first().id
    # transcript_from_DB = LecturesInfo.query.filter_by(id = transcript_id).first().video_transcript

    # get the answer from the question answering model
    predicted_answer = question_answering.get_answer(transcript=query_res[1].video_transcript, question=query)
    # Create a JSON response with the answer
    return jsonify({"answer": predicted_answer})

"""
uploaded_image: Handle getting the uploaded image via GET request
"""
@app.route("/uploads/Accounts_images/<path:filename>")
def uploaded_image(filename):
    return send_from_directory("uploads/Accounts_images",filename)
"""
uploaded_pdf: Handle getting the uploaded pdf via GET request
"""
@app.route("/uploads/Accounts_PDFs/<path:filename>")
def uploaded_pdf(filename):
    return send_from_directory("uploads/Accounts_PDFs", filename)
"""
summarize: Handle summarizing the lecture via POST request
"""
@app.route("/Summary", methods=["POST"])
def summarize():
    # get user id
    data = request.get_json()
    user_id = session.get("user_id")
    # get the last transcript chunks, video length, and transcript text from the client
    video_length = app.clients[user_id]["last_video_length"]
    transcript_chunks = app.clients[user_id]["last_transcript_chunks"]
    transcript_text = app.clients[user_id]["last_transcript_text"]

    summaries = []
    summaries_embeds = []
    segments = [] # replaced with None
    titles = []
   
    if video_length >= min_length_segmentation or force_segmentation: # if the video is longer than 10 minutes, or if the user forced segmentations.
        #### Segmentation

        segment_method = data['quality']

        start_time = time.time()
        if segment_method == 'highQuality':
            print("it will segment using the segmentation model")
            segments = segmentationModel.segment_the_transcript(transcript_chunks)

        elif segment_method == 'faster':
            print("it will segment using the segmentation algorithm")
            segments = segmentationAlgo.segment_the_transcript(transcript_chunks, video_length)

        end_time = time.time()
        #print("segmentation time: ", end_time-start_time)

        segments=sorted(segments)
        if len(segments) == 0:
            transcripts = [transcript_text]
        else:
            # get the transcripts part of each segment
            transcripts = []
            s=0
            for b in segments:
                #print("s: ", s,b)
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
                    #print('last segment is not the end of the video: ',transcript_chunks[-1]['end'] - segments[-1])
                    transcripts[-1] = transcripts[-1] + ' '+ ' '.join([x['text'] for x in transcript_chunks[s:]])

        titles,summaries = summarizer.summarize_segments(transcripts)
        summaries_embeds =  [x.tolist() for x in embeddor.get_embeddings(summaries)] 
    else:
        ## Summarizing the full video. Use one element arrays to be consistent with the segmentation case
        summary = summarizer.summarize(transcript_text)
        summary_embed = embeddor.get_embedding(summary)
        summaries.append(summary)
        summaries_embeds.append(summary_embed.tolist())
        titles = ['']
        segments=[0]
    segments_str = {}
    # if there are segments, format them
    if len(segments) > 1:
        segments_str = [{'end':s,'title':t} for s,t in zip(segments,titles)]
    # save the summary in the db, update the same row of the lecture
    user_id = session.get("user_id")
    lecture_id = app.clients[user_id]['last_video_id']
    lecture_info = LecturesInfo.query.filter_by(id=lecture_id).first()
    lecture_info.summary = summaries
    lecture_info.summary_vector = summaries_embeds
    lecture_info.segments = segments_str
    db.session.commit()
    # Create a JSON response with the summary
    return jsonify({"summaries":summaries,
                    "segment_titles":titles,
                    "segments":segments,
                    "segments_str":segments_str})

"""
generate_pdf: Handle generating the pdf via POST request
"""
@app.route('/generate_pdf', methods=['POST', 'GET'])
def generate_pdf():
    # get data from the request
    user_id = session.get("user_id")
    data = request.get_json()
    transcript = data.get('transcript')
    # summary = data.get('summary')
    url = data.get('title')
    # segments = db.session.query(LecturesInfo.segments).all()

    # If you want to filter by a specific condition, for example, lecture_name equals "YourLectureName":
    lecture_url = url
    # get the lecture segments and summary from the db
    segments = db.session.query(LecturesInfo.segments).filter(LecturesInfo.video_url == lecture_url).first()
    segments = segments.segments
    summary = db.session.query(LecturesInfo.summary).filter(LecturesInfo.video_url == lecture_url).first()
    summary = summary.summary
    thumbnail = db.session.query(LecturesInfo.thumbnail_image).filter(LecturesInfo.video_url == lecture_url).first()

    titles = [segment["title"] for segment in segments]
    # Create a new PDF document
    pdf = FPDF(format='letter')  # Change the format to a larger size if needed
    #image_path = "E:\\Senior\\LASER-main\\client\\src\\pages\\assets2\\search.jpeg"
    image_path = "E:\\Senior\\LASER-main\\backend\\uploads\\Accounts_images\\" + thumbnail.thumbnail_image
    pdf.set_title("My Summaries")  # Add your desired title here
    pdf.add_page()
    pdf.set_font('Times', 'B', 32)
    laser_spaces = " ".join("LASER")
    pdf.cell(0, 10, laser_spaces, 0, 1, 'C')
    pdf.image(image_path, x=10, y=pdf.get_y(), w=180)
    pdf.ln(181)
    pdf.set_font('Times', '', 25)
    pdf.cell(0, 10, 'Title :  ', ln=True,align="L")  # Change 'Transcript Title' to your desired title
    pdf.set_font('Times', '', 15)
    pdf.set_link(url)
    # add the lecture title
    pdf.multi_cell(0, 10, str(url),0,1,'C')  # Change 'Transcript Title' to your desired title

    pdf.add_page()


    # Add the title for the transcript
    pdf.set_font('Times', 'B', 25)
    pdf.cell(0, 10, 'Summaries', align="C")  # Change 'Transcript Title' to your desired title
    pdf.set_font('Arial', '', 12)

    pdf.ln(40)

    # Add the transcript content

    for i in range(len(summary)):
        pdf.set_font('Arial', '', 18)
        if i < len(titles):
         pdf.cell(0, 10, titles[i], 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, summary[i])
        pdf.ln(20)  
    # pdf.multi_cell(0, 10, transcript)
    pdf_output_path = "E:\\Senior\\LASER-main\\backend\\Downloads\\LASER Summaries.pdf"
    pdf.output(pdf_output_path)



    return send_file(pdf_output_path, download_name='LASER Summaries.pdf', as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True, port=5000,threaded=True) 