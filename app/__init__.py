# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from .fetch_data import fetch_odds

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Ensure the database is created and fetch initial data
    with app.app_context():
        db.create_all()
        print("[INFO] Database tables created")
        fetch_odds(db)  # Optional: Fetch odds once on startup

    # Set up APScheduler to run fetch_odds every 10 minutes
    def scheduled_job():
        print("[INFO] Scheduled job triggered")
        with app.app_context():
            fetch_odds(db)

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=scheduled_job, trigger="interval", minutes=30)
    scheduler.start()

    return app
