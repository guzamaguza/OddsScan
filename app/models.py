from . import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class OddsEvent(db.Model):
    __tablename__ = 'odds_events'
    
    id = db.Column(db.String, primary_key=True)  # event ID
    sport_key = db.Column(db.String, nullable=False)
    sport_title = db.Column(db.String, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    bookmakers = db.Column(JSON, nullable=True)  # store full JSON response

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, db.ForeignKey('odds_events.id'), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    scores = db.Column(JSON, nullable=True)  # stores the list of score dicts

    # Optional relationship (one-to-one or many-to-one)
    event = db.relationship('OddsEvent', backref=db.backref('score', uselist=False))


    # Relationship to Odds
    odds_entry = db.relationship("Odds", back_populates="score", uselist=False)

    def __repr__(self):
        return f"<Score(event_id={self.event_id}, completed={self.completed}, home_score={self.home_score}, away_score={self.away_score})>"
