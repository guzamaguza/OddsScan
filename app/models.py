from . import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from uuid import uuid4

class OddsEvent(db.Model):
    __tablename__ = 'odds_events'

    # NEW: Add a unique UUID for each row as the primary key
    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))

    # Keep the original event_id (from API), but allow duplicates
    id = db.Column(db.String, nullable=False)  # Event ID from API

    sport_key = db.Column(db.String, nullable=False)
    sport_title = db.Column(db.String, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    bookmakers = db.Column(JSON, nullable=True)  # Store full JSON response
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When this record was inserted


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    
    # This still points to OddsEvent.id (not uuid) — we can revisit this if needed
    event_id = db.Column(db.String, db.ForeignKey('odds_events.id'), nullable=False)

    completed = db.Column(db.Boolean, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    scores = db.Column(JSON, nullable=True)  # stores the list of score dicts
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    event = db.relationship('OddsEvent', backref=db.backref('scores', lazy=True))

    def __repr__(self):
        return f"<Score(event_id={self.event_id}, completed={self.completed}, created_at={self.created_at})>"
