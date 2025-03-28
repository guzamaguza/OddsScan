import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    DATABASE_URI = 'sqlite:///odds.db'  # Change to PostgreSQL/MySQL if needed
    DEBUG = True
