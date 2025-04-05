from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# We do NOT create db here. It should be imported from app
# from app import db  <-- You don't need to declare it again here, it's already initialized in app/__init__.py

class Event(db.Model):
    id = db.Column(db.String(10), primary_key=True)  # Adjust length of string if necessary
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Event {self.name}>"

class Odds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.String(10), db.ForeignKey('event.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    odds_value = db.Column(db.Float, nullable=False)

    event = db.relationship('Event', backref=db.backref('odds', lazy=True))

    def __repr__(self):
        return f"<Odds {self.odds_value} for Event {self.event_id}>"
