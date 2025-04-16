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
    # Get the event and its historical odds
    event = OddsEvent.query.get_or_404(uuid)
    historical_odds = event.historical_odds.order_by(HistoricalOdds.created_at.asc()).all()
    
    print(f"Debug: Found {len(historical_odds)} historical odds records for event {uuid}")
    
    # Get unique bookmaker names
    bookmaker_names = set()
    for odds in historical_odds:
        if odds.bookmakers:
            for bookmaker in odds.bookmakers:
                bookmaker_names.add(bookmaker.get('title'))
    # Also include current bookmakers
    if event.bookmakers:
        for bookmaker in event.bookmakers:
            bookmaker_names.add(bookmaker.get('title'))
    bookmaker_names = sorted(list(bookmaker_names))
    
    print(f"Debug: Found {len(bookmaker_names)} unique bookmakers: {bookmaker_names}")
    
    # Prepare data for the chart
    chart_data = {
        'labels': [],
        'commence_time': event.commence_time.strftime('%Y-%m-%d %H:%M:%S'),
        'bookmakers': bookmaker_names,
        'home_odds': {name: [] for name in bookmaker_names},
        'away_odds': {name: [] for name in bookmaker_names},
        'draw_odds': {name: [] for name in bookmaker_names}
    }
    
    # Add historical odds data
    for odds in historical_odds:
        created_at_utc = odds.created_at.replace(tzinfo=timezone.utc)
        chart_data['labels'].append(created_at_utc.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Initialize odds for this timestamp
        for bookmaker in bookmaker_names:
            chart_data['home_odds'][bookmaker].append(None)
            chart_data['away_odds'][bookmaker].append(None)
            chart_data['draw_odds'][bookmaker].append(None)
        
        # Get odds for each bookmaker
        if odds.bookmakers:
            for bookmaker in odds.bookmakers:
                bookmaker_name = bookmaker.get('title')
                if bookmaker_name in bookmaker_names:
                    for market in bookmaker.get('markets', []):
                        if market.get('key') == 'h2h':
                            for outcome in market.get('outcomes', []):
                                try:
                                    price = float(outcome.get('price'))
                                    if outcome.get('name') == event.home_team:
                                        chart_data['home_odds'][bookmaker_name][-1] = price
                                    elif outcome.get('name') == event.away_team:
                                        chart_data['away_odds'][bookmaker_name][-1] = price
                                    elif outcome.get('name') == 'Draw':
                                        chart_data['draw_odds'][bookmaker_name][-1] = price
                                except (ValueError, TypeError):
                                    print(f"Debug: Invalid price value for {bookmaker_name}: {outcome.get('price')}")
    
    # Add current odds data
    if event.bookmakers:
        current_time = datetime.now(timezone.utc)
        chart_data['labels'].append(current_time.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Initialize odds for current timestamp
        for bookmaker in bookmaker_names:
            chart_data['home_odds'][bookmaker].append(None)
            chart_data['away_odds'][bookmaker].append(None)
            chart_data['draw_odds'][bookmaker].append(None)
        
        # Get current odds for each bookmaker
        for bookmaker in event.bookmakers:
            bookmaker_name = bookmaker.get('title')
            if bookmaker_name in bookmaker_names:
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        for outcome in market.get('outcomes', []):
                            try:
                                price = float(outcome.get('price'))
                                if outcome.get('name') == event.home_team:
                                    chart_data['home_odds'][bookmaker_name][-1] = price
                                elif outcome.get('name') == event.away_team:
                                    chart_data['away_odds'][bookmaker_name][-1] = price
                                elif outcome.get('name') == 'Draw':
                                    chart_data['draw_odds'][bookmaker_name][-1] = price
                            except (ValueError, TypeError):
                                print(f"Debug: Invalid price value for {bookmaker_name}: {outcome.get('price')}")
    
    print(f"Debug: Generated chart data with {len(chart_data['labels'])} timestamps")
    print(f"Debug: Sample home odds: {chart_data['home_odds'][bookmaker_names[0] if bookmaker_names else '']}")
    print(f"Debug: Sample away odds: {chart_data['away_odds'][bookmaker_names[0] if bookmaker_names else '']}")
    
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
