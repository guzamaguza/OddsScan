# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Store db instance in app context
    app.db = db

    # Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Ensure the database is created and fetch initial data
    with app.app_context():
        db.create_all()
        print("[INFO] Database tables created")
        from app.fetch_data import fetch_all_data
        fetch_all_data(db)  # Fetch both odds and scores on startup

    # Set up APScheduler to run fetch_all_data every 10 minutes
    def scheduled_job():
        print("[INFO] Scheduled job triggered")
        with app.app_context():
            fetch_all_data(db)

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=scheduled_job, trigger="interval", minutes=10)
    scheduler.start()

    return app
