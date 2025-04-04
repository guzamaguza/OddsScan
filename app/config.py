import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    DATABASE_URI = 'sqlite:///odds.db'  # Change to PostgreSQL/MySQL if needed
    DEBUG = True


from flask_sqlalchemy import SQLAlchemy


# Get database URL from environment variable (set on Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure the app doesn’t run without a valid database URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Make sure you configured it in Render.")

# Flask Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

