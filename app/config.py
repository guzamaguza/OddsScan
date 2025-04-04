import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # This should already be in use
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ODDS_API_KEY = os.getenv("ODDS_API_KEY")  # Your new variable
