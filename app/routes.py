# app/routes.py
from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "API is up!"

@main.route("/events")
def events():
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}
