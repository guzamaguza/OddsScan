from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from .fetch_data import fetch_odds  # Import the fetch_odds function from fetch_data.py
from .routes import main  # Import the main blueprint

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register the main blueprint
    app.register_blueprint(main)

    # Set up APScheduler to run fetch_odds every 10 minutes
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=fetch_odds, trigger="interval", minutes=10)
    scheduler.start()

    # Ensure the database is created when the app starts
    with app.app_context():
        db.create_all()  # Create all tables
        print("[INFO] Database tables created")

    return app
