from dotenv import load_dotenv
import os
import redis

load_dotenv()


# Configuration class for the application settings.
class ApplicationConfig:
    # Secret key retrieved from environment variable for security.
    SECRET_KEY = os.environ["SECRET_KEY"]

    # SQLAlchemy settings to disable modification tracking, enable echoing, and set the database URI.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    # Session configuration using Redis for type, non-permanent sessions, signer usage, and Redis server URL.
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379/")

