from app import db
from datetime import datetime

class Odds(db.Model):
    __tablename__ = 'odds'
    __table_args__ = (
        db.UniqueConstraint('game_id', 'bookmakers', 'market', 'outcome', name='unique_odds_entry'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String, nullable=False, unique=True)  # Changed from event_id to game_id
    sport_key = db.Column(db.String, nullable=False)
    sport_title = db.Column(db.String, nullable=False)
    commence_time = db.Column(db.DateTime, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    bookmakers = db.Column(db.JSON, nullable=True)  # Stores bookmakers in JSON format
    link = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship with Score table
    score = db.relationship("Score", back_populates="odds_entry", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Odds(game_id={self.game_id}, home_team={self.home_team}, away_team={self.away_team})>"

class Score(db.Model):
    __tablename__ = 'scores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String, db.ForeignKey('odds.game_id'), nullable=False, unique=True)  # Changed from event_id to game_id
    completed = db.Column(db.Boolean, nullable=False, default=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    # Relationship to Odds
    odds_entry = db.relationship("Odds", back_populates="score", uselist=False)

    def __repr__(self):
        return f"<Score(game_id={self.game_id}, completed={self.completed}, home_score={self.home_score}, away_score={self.away_score})>"

