from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta, timezone
from app.models import OddsEvent, Score, HistoricalOdds
from sqlalchemy import func
from app import db

main = Blueprint("main", __name__)

@main.route('/')
def home():
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    
    # Get past events (completed more than 2 hours ago)
    past_events = OddsEvent.query.filter(
        OddsEvent.commence_time < (now - timedelta(hours=2))
    ).order_by(OddsEvent.commence_time.desc()).all()
    
    # Get ongoing events (started but not completed)
    ongoing_events = OddsEvent.query.filter(
        OddsEvent.commence_time <= now,
        OddsEvent.commence_time > (now - timedelta(hours=2))
    ).order_by(OddsEvent.commence_time.asc()).all()
    
    # Get upcoming events (not started yet)
    upcoming_events = OddsEvent.query.filter(
        OddsEvent.commence_time > now
    ).order_by(OddsEvent.commence_time.asc()).all()
    
    # Remove duplicates based on event ID
    def remove_duplicates(events):
        seen = set()
        unique_events = []
        for event in events:
            if event.id not in seen:
                seen.add(event.id)
                unique_events.append(event)
        return unique_events
    
    # Remove duplicates and sort each category
    past_events = sorted(remove_duplicates(past_events), key=lambda x: x.commence_time, reverse=True)
    ongoing_events = sorted(remove_duplicates(ongoing_events), key=lambda x: x.commence_time)
    upcoming_events = sorted(remove_duplicates(upcoming_events), key=lambda x: x.commence_time)
    
    # Debug logging
    print(f"Current time (UTC): {now}")
    print(f"Past events count: {len(past_events)}")
    print(f"Ongoing events count: {len(ongoing_events)}")
    print(f"Upcoming events count: {len(upcoming_events)}")
    
    return render_template('home.html', 
                         past_events=past_events,
                         ongoing_events=ongoing_events,
                         upcoming_events=upcoming_events)

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
    """Get historical odds data for a specific event"""
    from app.models import OddsEvent, HistoricalOdds
    from datetime import datetime, timezone

    print(f"\n[DEBUG] Fetching odds history for event: {uuid}")
    
    # Get the event
    event = OddsEvent.query.filter_by(uuid=uuid).first()
    if not event:
        print(f"[ERROR] Event {uuid} not found")
        return jsonify({"error": "Event not found"}), 404

    print(f"[DEBUG] Found event: {event.uuid}")
    print(f"- Home Team: {event.home_team}")
    print(f"- Away Team: {event.away_team}")
    print(f"- Current Bookmakers: {len(event.bookmakers) if event.bookmakers else 0}")

    # Get historical odds
    historical_odds = HistoricalOdds.query.filter_by(event_id=uuid).order_by(HistoricalOdds.created_at).all()
    print(f"[DEBUG] Found {len(historical_odds)} historical odds records")

    # Collect all unique bookmaker names
    bookmaker_names = set()
    if event.bookmakers:
        for bookmaker in event.bookmakers:
            bookmaker_names.add(bookmaker["key"])
    for history in historical_odds:
        if history.bookmakers:
            for bookmaker in history.bookmakers:
                bookmaker_names.add(bookmaker["key"])
    bookmaker_names = sorted(list(bookmaker_names))
    print(f"[DEBUG] Found {len(bookmaker_names)} unique bookmakers: {bookmaker_names}")

    # Initialize chart data structure
    chart_data = {
        "labels": [],  # Timestamps
        "datasets": {
            "home": {name: [] for name in bookmaker_names},
            "away": {name: [] for name in bookmaker_names}
        }
    }

    # Process historical odds
    for history in historical_odds:
        if not history.bookmakers:
            continue
            
        timestamp = history.created_at.strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(timestamp)
        
        # Process each bookmaker's odds
        for bookmaker in history.bookmakers:
            if bookmaker["key"] not in bookmaker_names:
                continue
                
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        if outcome["name"] == event.home_team:
                            chart_data["datasets"]["home"][bookmaker["key"]].append(price)
                        elif outcome["name"] == event.away_team:
                            chart_data["datasets"]["away"][bookmaker["key"]].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Add current odds
    if event.bookmakers:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(current_time)
        
        for bookmaker in event.bookmakers:
            if bookmaker["key"] not in bookmaker_names:
                continue
                
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        if outcome["name"] == event.home_team:
                            chart_data["datasets"]["home"][bookmaker["key"]].append(price)
                        elif outcome["name"] == event.away_team:
                            chart_data["datasets"]["away"][bookmaker["key"]].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Ensure all arrays have the same length
    max_length = len(chart_data["labels"])
    for team in ["home", "away"]:
        for bookmaker in bookmaker_names:
            while len(chart_data["datasets"][team][bookmaker]) < max_length:
                chart_data["datasets"][team][bookmaker].append(None)

    print(f"[DEBUG] Generated chart data:")
    print(f"- Timestamps: {len(chart_data['labels'])}")
    print(f"- Sample home odds: {[chart_data['datasets']['home'][name][-1] for name in bookmaker_names]}")
    print(f"- Sample away odds: {[chart_data['datasets']['away'][name][-1] for name in bookmaker_names]}")

    return jsonify(chart_data)

@main.route("/events")
def events():
    # Return a list of all events' ids as JSON
    from app.models import OddsEvent
    return {"events": [e.id for e in OddsEvent.query.all()]}

@main.route("/debug/events")
def debug_events():
    events = OddsEvent.query.order_by(OddsEvent.commence_time.asc()).all()
    now = datetime.now(timezone.utc)
    
    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'home_team': event.home_team,
            'away_team': event.away_team,
            'commence_time': event.commence_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'is_past': event.commence_time < (now - timedelta(hours=2)),
            'is_ongoing': (event.commence_time <= now and event.commence_time > (now - timedelta(hours=2))),
            'is_upcoming': event.commence_time > now
        })
    
    return jsonify({
        'current_time': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'events': event_data
    })
