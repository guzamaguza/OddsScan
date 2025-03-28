from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Odds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(10), db.ForeignKey('event.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    odds_value = db.Column(db.Float, nullable=False)

    event = db.relationship('Event', backref=db.backref('odds', lazy=True))
