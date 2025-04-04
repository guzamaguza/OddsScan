import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Use Render's default
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ODDS_API_KEY = os.environ.get('ODDS_API_KEY')

