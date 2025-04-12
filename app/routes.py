# app/routes.py
from flask import Blueprint

main = Blueprint("main", __name__)

@main.route('/')
def home():
    # Get current time
    now = datetime.utcnow()

    # Get past, ongoing, and future events
    past_events = OddsEvent.query.filter(OddsEvent.commence_time < now).all()
    ongoing_events = OddsEvent.query.filter(OddsEvent.commence_time <= now, OddsEvent.commence_time >= now).all()
    future_events = OddsEvent.query.filter(OddsEvent.commence_time > now).all()

    return render_template('home.html', past_events=past_events, ongoing_events=ongoing_events, future_events=future_events)

@main.route("/events")
def events():
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}

