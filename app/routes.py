from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
from app.models import OddsEvent, Score
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

@main.route("/match/<uuid>")
def match_details(uuid):
    # Get the event and its associated score
    event = OddsEvent.query.get_or_404(uuid)
    score = Score.query.filter_by(event_id=uuid).first()
    
    return render_template('match_details.html', 
                         event=event,
                         score=score)

@main.route("/match/<uuid>/odds-history")
def odds_history(uuid):
    # Get all historical odds for this event (using the API event ID)
    event = OddsEvent.query.get_or_404(uuid)
    historical_events = OddsEvent.query.filter_by(id=event.id).order_by(OddsEvent.created_at.asc()).all()
    
    # Prepare data for the chart
    chart_data = {
        'labels': [],
        'home_odds': [],
        'away_odds': [],
        'draw_odds': [],
        'commence_time': event.commence_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    for event in historical_events:
        # Convert created_at to UTC for consistent comparison
        created_at_utc = event.created_at.astimezone(datetime.timezone.utc)
        chart_data['labels'].append(created_at_utc.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Get the best odds for each outcome
        home_odds = None
        away_odds = None
        draw_odds = None
        
        if event.bookmakers:
            for bookmaker in event.bookmakers:
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        for outcome in market.get('outcomes', []):
                            if outcome.get('name') == event.home_team:
                                if home_odds is None or outcome.get('price', 0) > home_odds:
                                    home_odds = outcome.get('price')
                            elif outcome.get('name') == event.away_team:
                                if away_odds is None or outcome.get('price', 0) > away_odds:
                                    away_odds = outcome.get('price')
                            elif outcome.get('name') == 'Draw':
                                if draw_odds is None or outcome.get('price', 0) > draw_odds:
                                    draw_odds = outcome.get('price')
        
        # Ensure we have valid numbers for the chart
        chart_data['home_odds'].append(float(home_odds) if home_odds is not None else None)
        chart_data['away_odds'].append(float(away_odds) if away_odds is not None else None)
        chart_data['draw_odds'].append(float(draw_odds) if draw_odds is not None else None)
    
    return jsonify(chart_data)

@main.route("/events")
def events():
    # Return a list of all events' ids as JSON
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}
