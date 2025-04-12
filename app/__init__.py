from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from .fetch_data import fetch_odds  # Import the fetch_odds function from fetch_data.py

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        fetch_odds()  # ✅ Run once on startup

    # Set up APScheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=fetch_odds, trigger="interval", minutes=10)
    scheduler.start()

    from .routes import main
    app.register_blueprint(main)

    return app

