from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask import Flask

db = SQLAlchemy()

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

def create_app():
    # Load environment variables first
    load_dotenv()

    app = Flask(__name__)

    # ✅ Set the database URI from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Initialize the database
    db.init_app(app)

    # Optional test route
    @app.route('/')
    def index():
        return "✅ Flask App is running and connected to PostgreSQL!"

    return app

