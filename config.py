import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Make sure this is set in Render
    SQLALCHEMY_TRACK_MODIFICATIONS = False
