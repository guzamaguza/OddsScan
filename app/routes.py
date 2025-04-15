from flask import Blueprint, render_template
from datetime import datetime, timedelta
from app.models import OddsEvent
from sqlalchemy import func
from app import db

main = Blueprint("main", __name__)

@main.route('/')
def home():
    # Get current time
    now = datetime.utcnow()
    
    # Define a time window for ongoing events (e.g., events that started in the last 3 hours)
    ongoing_window = timedelta(hours=3)
    ongoing_start = now - ongoing_window

    # Get past events (events that ended before the ongoing window)
    past_events = OddsEvent.query.filter(
        OddsEvent.commence_time < ongoing_start
    ).order_by(OddsEvent.commence_time.desc()).all()

    # Get ongoing events (events that started within the ongoing window)
    ongoing_events = OddsEvent.query.filter(
        OddsEvent.commence_time >= ongoing_start,
        OddsEvent.commence_time <= now
    ).order_by(OddsEvent.commence_time.asc()).all()

    # Get future events
    future_events = OddsEvent.query.filter(
        OddsEvent.commence_time > now
    ).order_by(OddsEvent.commence_time.asc()).all()

    # Remove duplicates based on id, keeping the most recent version
    def remove_duplicates(events):
        seen = set()
        unique_events = []
        for event in events:
            if event.id not in seen:
                seen.add(event.id)
                unique_events.append(event)
        return unique_events

    past_events = remove_duplicates(past_events)
    ongoing_events = remove_duplicates(ongoing_events)
    future_events = remove_duplicates(future_events)

    return render_template('home.html', 
                         past_events=past_events, 
                         ongoing_events=ongoing_events, 
                         future_events=future_events)

@main.route("/events")
def events():
    # Return a list of all events' ids as JSON
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}
