from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from app.utils import fetch_and_store_odds, fetch_and_store_scores, start_scheduler, ODDS_URL, SPORT

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configs from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Trigger data fetching on startup
    with app.app_context():
        print("[DEBUG] Fetching odds and scores on startup...")
        fetch_and_store_odds(ODDS_URL, SPORT)  # Fetch odds using constants
        fetch_and_store_scores()  # Fetch scores
        start_scheduler()  # Start scheduler for recurring fetches

    return app



