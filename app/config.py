import os
from flask_sqlalchemy import SQLAlchemy


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Use Render's PostgreSQL URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False


