from app import db

class Odds(db.Model):
    __tablename__ = 'odds'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, nullable=False)
    home_team = db.Column(db.String, nullable=False)
    away_team = db.Column(db.String, nullable=False)
    commence_time = db.Column(db.String, nullable=False)
    bookmaker = db.Column(db.String, nullable=False)
    market = db.Column(db.String, nullable=False)
    outcome = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    point = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.String, nullable=False)
    odds_type = db.Column(db.String, nullable=False)

    # Optional relationship to scores
    score = db.relationship("Score", backref="odds", lazy=True, uselist=False, primaryjoin="Odds.event_id == Score.event_id")


class Score(db.Model):
    __tablename__ = 'scores'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, db.ForeignKey('odds.event_id'), nullable=False, unique=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)

    





