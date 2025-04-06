from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask import Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Initialize the database object globally
db = SQLAlchemy()

def create_app():
    # Load environment variables
    load_dotenv()

    # Create Flask app
    app = Flask(__name__)

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Import routes here to avoid circular import
    from app.routes import main
    app.register_blueprint(main)

    return app



class Odds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(100), nullable=False)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(100), nullable=False)
    bookmaker = db.Column(db.String(100), nullable=False)
    market = db.Column(db.String(50), nullable=False)
    outcome = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    point = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.String(100), nullable=False)
    odds_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Odds {self.event_id} - {self.home_team} vs {self.away_team}>'

