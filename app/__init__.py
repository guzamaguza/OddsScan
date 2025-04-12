from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app


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



