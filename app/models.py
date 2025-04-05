from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db
# We do NOT create db here. It should be imported from app
# from app import db  <-- You don't need to declare it again here, it's already initialized in app/__init__.py

class Event(db.Model):
    __tablename__ = 'event'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100))
    odds = db.relationship('Odds', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.name}>'

class Odds(db.Model):
    __tablename__ = 'odds'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(50), db.ForeignKey('event.id'), nullable=False)
    time = db.Column(db.String(50))
    odds_value = db.Column(db.Float)

    def __repr__(self):
        return f'<Odds {self.odds_value}>'




