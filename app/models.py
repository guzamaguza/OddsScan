from app import db

class Odds(db.Model):
    __tablename__ = 'odds'
    __table_args__ = {'extend_existing': True}  # Add this line to allow altering the table schema

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

    # New fields
    completed = db.Column(db.Boolean, nullable=False, default=False)  # Indicates if the event is completed
    home_score = db.Column(db.Integer, nullable=True)  # Stores the home team's score
    away_score = db.Column(db.Integer, nullable=True)  # Stores the away team's score

    





