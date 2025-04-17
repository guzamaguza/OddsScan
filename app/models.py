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

class HistoricalOdds(db.Model):
    __tablename__ = 'historical_odds'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, db.ForeignKey('odds_events.uuid'), nullable=False)
    bookmakers = db.Column(JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    event = db.relationship('OddsEvent', backref=db.backref('historical_odds', lazy=True))

    def __repr__(self):
        return f"<HistoricalOdds(event_id={self.event_id}, created_at={self.created_at})>"

class Score(db.Model):
    """Model for storing game scores"""
    __tablename__ = 'scores'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(36), db.ForeignKey('odds_events.uuid'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    scores = db.Column(db.JSON, nullable=True)
    
    # Relationship with OddsEvent
    event = db.relationship('OddsEvent', backref=db.backref('score', uselist=False))
    
    def __repr__(self):
        return f"<Score {self.id}: {self.home_team} vs {self.away_team}>"
