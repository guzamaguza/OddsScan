from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Setup configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the database
    db.init_app(app)

    # Register blueprints
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

