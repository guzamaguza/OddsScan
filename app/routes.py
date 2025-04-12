from flask import Blueprint, render_template
from datetime import datetime
from app.models import OddsEvent

main = Blueprint("main", __name__)

@main.route('/')
def home():
    # Get current time
    now = datetime.utcnow()

    # Get past, ongoing, and future events (ensure unique events with distinct)
    past_events = OddsEvent.query.filter(OddsEvent.commence_time < now).distinct().all()
    ongoing_events = OddsEvent.query.filter(OddsEvent.commence_time <= now, OddsEvent.commence_time >= now).distinct().all()
    future_events = OddsEvent.query.filter(OddsEvent.commence_time > now).distinct().all()

    return render_template('home.html', past_events=past_events, ongoing_events=ongoing_events, future_events=future_events)

@main.route("/events")
def events():
    # Return a list of all events' ids as JSON
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}
