from . import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from uuid import uuid4

class OddsEvent(db.Model):
    __tablename__ = 'odds_events'

    uuid = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    id = db.Column(db.String, nullable=False)  # Event ID from API
    sport_key = db.Column(db.String, nullable=False)
    sport_title = db.Column(db.String, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    bookmakers = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<OddsEvent(uuid={self.uuid}, home_team={self.home_team}, away_team={self.away_team})>"

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, db.ForeignKey('odds_events.uuid'), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    scores = db.Column(JSON, nullable=True)

    event = db.relationship('OddsEvent', backref=db.backref('scores', lazy=True))

    def __repr__(self):
        return f"<Score(event_id={self.event_id}, completed={self.completed})"
