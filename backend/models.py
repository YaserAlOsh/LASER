# Import necessary modules and libraries.
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

# Create a SQLAlchemy instance.
db = SQLAlchemy()

# Function to generate and return a UUID.
def get_uuid():
    return uuid4().hex

# Define the User model for the 'users' table.
class User(db.Model):
    __tablename__ = "users"
    
    # User table columns: id, username, email, password.
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)

# Define the UsersLectures model for the 'users_lectures' table.
class UsersLectures(db.Model):
    __tablename__ = "users_lectures"
    
    # UsersLectures table columns: id, user_id (foreign key to User), upload_date.
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=True)

# Define the LecturesInfo model for the 'lectures_info' table.
class LecturesInfo(db.Model):
    __tablename__ = "lectures_info"
    
    # LecturesInfo table columns: id (foreign key to UsersLectures), lecture_name, video_url, video_transcript, summary, segments, tags, summary_vector, thumbnail_image.
    id = db.Column(db.String(32), db.ForeignKey('users_lectures.id'), primary_key=True, unique=True, default=get_uuid)
    lecture_name = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.Text, nullable=False)
    video_transcript = db.Column(db.Text, nullable=False)
    summary = db.Column(db.JSON, nullable=False)
    segments = db.Column(db.JSON, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    summary_vector = db.Column(db.JSON, nullable=False)
    thumbnail_image = db.Column(db.Text, nullable=True)
    # Additional fields that can be added: thumbnail_url, notes.
