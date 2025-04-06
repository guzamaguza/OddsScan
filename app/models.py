from . import db

class Odds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String)
    home_team = db.Column(db.String)
    away_team = db.Column(db.String)
    start_time = db.Column(db.String)
    bookmaker = db.Column(db.String)
    market = db.Column(db.String)
    outcome = db.Column(db.String)
    price = db.Column(db.Float)
    point = db.Column(db.Float)
    timestamp = db.Column(db.String)
    odds_type = db.Column(db.String)



