from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta, timezone
from app.models import OddsEvent, Score, HistoricalOdds
from sqlalchemy import func, desc
from app import db
import uuid

main = Blueprint('main', __name__)

@main.route('/')
def home():
    now = datetime.utcnow()
    
    # Get all events from the last 24 hours
    events = OddsEvent.query.filter(
        OddsEvent.commence_time > (now - timedelta(days=1))
    ).order_by(desc(OddsEvent.commence_time)).all()
    
    # If no events found, create some mock events
    if not events:
        print("[INFO] No events found in database. Creating mock events.")
        from app.fetch_data import generate_mock_odds
        mock_data = generate_mock_odds()
        for event_data in mock_data:
            event = OddsEvent(
                uuid=str(uuid.uuid4()),
                id=event_data['id'],
                sport_key=event_data['sport_key'],
                sport_title=event_data['sport_title'],
                commence_time=datetime.fromisoformat(event_data['commence_time'].replace('Z', '+00:00')),
                home_team=event_data['home_team'],
                away_team=event_data['away_team'],
                bookmakers=event_data['bookmakers']
            )
            db.session.add(event)
        try:
            db.session.commit()
            events = OddsEvent.query.filter(
                OddsEvent.commence_time > (now - timedelta(days=1))
            ).order_by(desc(OddsEvent.commence_time)).all()
        except Exception as e:
            print(f"[ERROR] Failed to create mock events: {e}")
            db.session.rollback()
    
    # Remove duplicates based on event ID
    def remove_duplicates(events):
        seen = set()
        unique_events = []
        for event in events:
            if event.id not in seen:
                seen.add(event.id)
                unique_events.append(event)
        return unique_events
    
    # Remove duplicates and sort by time
    events = sorted(remove_duplicates(events), key=lambda x: x.commence_time, reverse=True)
    
    # Debug logging
    print(f"Current time (UTC): {now}")
    print(f"Total events count: {len(events)}")
    
    return render_template('home.html', 
                         events=events,
                         now=now)

@main.route("/match/<uuid>")
def match_details(uuid):
    event = OddsEvent.query.filter_by(uuid=uuid).first_or_404()
    score = Score.query.filter_by(event_id=uuid).first()
    return render_template('match_details.html', event=event, score=score)

@main.route("/match/<uuid>/odds-history")
def odds_history(uuid):
    event = OddsEvent.query.filter_by(uuid=uuid).first_or_404()
    
    # Get historical odds for this event
    historical_odds = HistoricalOdds.query.filter_by(event_id=uuid).order_by(HistoricalOdds.created_at).all()
    
    # Get unique bookmaker names from both current and historical odds
    bookmaker_names = set()
    if event.bookmakers:
        for bookmaker in event.bookmakers:
            bookmaker_names.add(bookmaker['title'])
    
    for historical in historical_odds:
        if historical.bookmakers:
            for bookmaker in historical.bookmakers:
                bookmaker_names.add(bookmaker['title'])
    
    # Prepare chart data
    chart_data = {
        'labels': [],  # Timestamps
        'datasets': []  # Bookmaker odds
    }
    
    # Add current odds
    if event.bookmakers:
        for bookmaker in event.bookmakers:
            if 'markets' in bookmaker and bookmaker['markets']:
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h' and 'outcomes' in market:
                        for outcome in market['outcomes']:
                            if outcome['name'] == event.home_team:
                                chart_data['labels'].append(event.updated_at.isoformat() if event.updated_at else event.commence_time.isoformat())
                                chart_data['datasets'].append({
                                    'label': f"{bookmaker['title']} - {event.home_team}",
                                    'data': [outcome['price']],
                                    'borderColor': 'rgba(75, 192, 192, 1)',
                                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                                })
                            elif outcome['name'] == event.away_team:
                                chart_data['labels'].append(event.updated_at.isoformat() if event.updated_at else event.commence_time.isoformat())
                                chart_data['datasets'].append({
                                    'label': f"{bookmaker['title']} - {event.away_team}",
                                    'data': [outcome['price']],
                                    'borderColor': 'rgba(255, 99, 132, 1)',
                                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                                })
    
    # Add historical odds
    for historical in historical_odds:
        if historical.bookmakers:
            for bookmaker in historical.bookmakers:
                if 'markets' in bookmaker and bookmaker['markets']:
                    for market in bookmaker['markets']:
                        if market['key'] == 'h2h' and 'outcomes' in market:
                            for outcome in market['outcomes']:
                                if outcome['name'] == event.home_team:
                                    chart_data['labels'].append(historical.created_at.isoformat())
                                    chart_data['datasets'].append({
                                        'label': f"{bookmaker['title']} - {event.home_team}",
                                        'data': [outcome['price']],
                                        'borderColor': 'rgba(75, 192, 192, 1)',
                                        'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                                    })
                                elif outcome['name'] == event.away_team:
                                    chart_data['labels'].append(historical.created_at.isoformat())
                                    chart_data['datasets'].append({
                                        'label': f"{bookmaker['title']} - {event.away_team}",
                                        'data': [outcome['price']],
                                        'borderColor': 'rgba(255, 99, 132, 1)',
                                        'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                                    })
    
    return jsonify(chart_data)

@main.route("/events")
def events():
    now = datetime.utcnow()
    events = OddsEvent.query.filter(
        OddsEvent.commence_time > (now - timedelta(days=1))
    ).order_by(desc(OddsEvent.commence_time)).all()
    return jsonify([{
        'uuid': event.uuid,
        'id': event.id,
        'sport_title': event.sport_title,
        'commence_time': event.commence_time.isoformat(),
        'home_team': event.home_team,
        'away_team': event.away_team,
        'bookmakers': event.bookmakers
    } for event in events])

@main.route("/debug/events")
def debug_events():
    now = datetime.utcnow()
    events = OddsEvent.query.filter(
        OddsEvent.commence_time > (now - timedelta(days=1))
    ).order_by(desc(OddsEvent.commence_time)).all()
    
    debug_info = []
    for event in events:
        score = Score.query.filter_by(event_id=event.uuid).first()
        debug_info.append({
            'uuid': event.uuid,
            'id': event.id,
            'sport_title': event.sport_title,
            'commence_time': event.commence_time.isoformat(),
            'home_team': event.home_team,
            'away_team': event.away_team,
            'bookmakers_count': len(event.bookmakers) if event.bookmakers else 0,
            'score': score.scores if score else None,
            'completed': score.completed if score else False
        })
    
    return jsonify(debug_info)

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
