from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta, timezone
from app.models import OddsEvent, Score, HistoricalOdds
from sqlalchemy import func, desc
from app import db

main = Blueprint("main", __name__)

@main.route('/')
def home():
    now = datetime.utcnow()
    
    # Get all events from the last 24 hours
    events = OddsEvent.query.filter(
        OddsEvent.commence_time > (now - timedelta(days=1))
    ).order_by(desc(OddsEvent.commence_time)).all()
    
    # Group events by sport
    events_by_sport = {}
    for event in events:
        if event.sport_title not in events_by_sport:
            events_by_sport[event.sport_title] = []
        events_by_sport[event.sport_title].append(event)
    
    return render_template('home.html', 
                         events_by_sport=events_by_sport,
                         now=now)

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

    # Get historical odds
    historical_odds = HistoricalOdds.query.filter_by(event_id=uuid).order_by(HistoricalOdds.created_at).all()
    print(f"[DEBUG] Found {len(historical_odds)} historical odds records")

    # Initialize chart data structure
    chart_data = {
        "labels": [],  # Timestamps
        "datasets": []  # List of datasets
    }

    # Process historical odds
    for history in historical_odds:
        if not history.bookmakers:
            continue
            
        timestamp = history.created_at.strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(timestamp)
        
        # Process each bookmaker's odds
        for bookmaker in history.bookmakers:
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        # Add to appropriate dataset
                        dataset_name = f"{bookmaker['key']} - {outcome['name']}"
                        dataset = next((d for d in chart_data["datasets"] if d["label"] == dataset_name), None)
                        
                        if not dataset:
                            dataset = {
                                "label": dataset_name,
                                "data": [],
                                "borderColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "backgroundColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "fill": False,
                                "tension": 0.1,
                                "pointRadius": 6,
                                "pointHoverRadius": 8,
                                "pointBackgroundColor": "white",
                                "pointBorderWidth": 2
                            }
                            chart_data["datasets"].append(dataset)
                        
                        dataset["data"].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Add current odds
    if event.bookmakers:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(current_time)
        
        for bookmaker in event.bookmakers:
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        # Add to appropriate dataset
                        dataset_name = f"{bookmaker['key']} - {outcome['name']}"
                        dataset = next((d for d in chart_data["datasets"] if d["label"] == dataset_name), None)
                        
                        if not dataset:
                            dataset = {
                                "label": dataset_name,
                                "data": [],
                                "borderColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "backgroundColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "fill": False,
                                "tension": 0.1,
                                "pointRadius": 6,
                                "pointHoverRadius": 8,
                                "pointBackgroundColor": "white",
                                "pointBorderWidth": 2
                            }
                            chart_data["datasets"].append(dataset)
                        
                        dataset["data"].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Ensure all datasets have the same length
    max_length = len(chart_data["labels"])
    for dataset in chart_data["datasets"]:
        while len(dataset["data"]) < max_length:
            dataset["data"].append(None)

    print(f"[DEBUG] Generated chart data:")
    print(f"- Timestamps: {len(chart_data['labels'])}")
    print(f"- Datasets: {len(chart_data['datasets'])}")
    for dataset in chart_data["datasets"]:
        print(f"- {dataset['label']}: {len(dataset['data'])} points")

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

@main.route("/debug/database")
def debug_database():
    """Debug route to check database contents"""
    from app.models import OddsEvent, HistoricalOdds, Score
    from datetime import datetime, timezone
    
    # Get counts
    odds_events = OddsEvent.query.count()
    historical_odds = HistoricalOdds.query.count()
    scores = Score.query.count()
    
    # Get sample data
    sample_event = OddsEvent.query.first()
    sample_history = HistoricalOdds.query.first()
    sample_score = Score.query.first()
    
    # Get current time
    now = datetime.now(timezone.utc)
    
    # Get event status counts
    past_events = OddsEvent.query.filter(OddsEvent.commence_time < (now - timedelta(hours=2))).count()
    ongoing_events = OddsEvent.query.filter(
        OddsEvent.commence_time <= now,
        OddsEvent.commence_time > (now - timedelta(hours=2))
    ).count()
    upcoming_events = OddsEvent.query.filter(OddsEvent.commence_time > now).count()
    
    return jsonify({
        "counts": {
            "odds_events": odds_events,
            "historical_odds": historical_odds,
            "scores": scores,
            "past_events": past_events,
            "ongoing_events": ongoing_events,
            "upcoming_events": upcoming_events
        },
        "sample_event": {
            "uuid": sample_event.uuid if sample_event else None,
            "home_team": sample_event.home_team if sample_event else None,
            "away_team": sample_event.away_team if sample_event else None,
            "commence_time": sample_event.commence_time.strftime('%Y-%m-%d %H:%M:%S UTC') if sample_event else None,
            "bookmakers_count": len(sample_event.bookmakers) if sample_event and sample_event.bookmakers else 0
        },
        "sample_history": {
            "id": sample_history.id if sample_history else None,
            "event_id": sample_history.event_id if sample_history else None,
            "created_at": sample_history.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if sample_history else None,
            "bookmakers_count": len(sample_history.bookmakers) if sample_history and sample_history.bookmakers else 0
        },
        "sample_score": {
            "id": sample_score.id if sample_score else None,
            "event_id": sample_score.event_id if sample_score else None,
            "completed": sample_score.completed if sample_score else None,
            "scores": sample_score.scores if sample_score else None
        }
    })
