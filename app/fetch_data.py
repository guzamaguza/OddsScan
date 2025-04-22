import requests
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import uuid
from flask import current_app
from app import db
from app.models import OddsEvent, Score, HistoricalOdds

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"

def fetch_odds():
    """Fetch odds data from the API and store in database"""
    api_key = current_app.config['ODDS_API_KEY']
    regions = 'us'  # Only US odds
    markets = 'h2h'  # Only head-to-head markets
    
    try:
        # Fetch NBA odds
        response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/basketball_nba/odds',
            params={
                'apiKey': api_key,
                'regions': regions,
                'markets': markets
            }
        )
        
        if response.status_code == 401:
            print("API key invalid. Using mock data for testing.")
            mock_data = generate_mock_odds()
            process_odds_data(mock_data)
            return
        elif response.status_code == 429:
            print("API quota reached. Using mock data for testing.")
            mock_data = generate_mock_odds()
            process_odds_data(mock_data)
            return
        elif response.status_code != 200:
            print("Error fetching NBA odds:", response.text)
            print("Using mock data for testing.")
            mock_data = generate_mock_odds()
            process_odds_data(mock_data)
            return
            
        odds_data = response.json()
        if not odds_data:
            print("No odds data returned. Using mock data for testing.")
            mock_data = generate_mock_odds()
            process_odds_data(mock_data)
            return
            
        process_odds_data(odds_data)
        
    except Exception as e:
        print("Error processing NBA odds:", str(e))
        print("Using mock data for testing.")
        mock_data = generate_mock_odds()
        process_odds_data(mock_data)
        db.session.rollback()

def generate_mock_odds():
    """Generate mock odds data for testing when API is unavailable"""
    from datetime import datetime, timedelta, timezone
    
    mock_events = []
    teams = [
        ('Lakers', 'Warriors'),
        ('Celtics', 'Bucks'),
        ('Nets', '76ers'),
        ('Heat', 'Knicks')
    ]
    
    now = datetime.now(timezone.utc)
    
    for i, (home, away) in enumerate(teams):
        commence_time = now + timedelta(hours=i)
        mock_events.append({
            'id': f'mock_nba_{i}',
            'sport_key': 'basketball_nba',
            'sport_title': 'NBA',
            'commence_time': commence_time.isoformat(),
            'home_team': home,
            'away_team': away,
            'bookmakers': [
                {
                    'key': 'mock_bookmaker',
                    'title': 'Mock Bookmaker',
                    'markets': [
                        {
                            'key': 'h2h',
                            'outcomes': [
                                {'name': home, 'price': 1.8 + (i * 0.1)},
                                {'name': away, 'price': 2.0 - (i * 0.1)}
                            ]
                        }
                    ]
                }
            ]
        })
    
    return mock_events

def process_odds_data(odds_data):
    """Process odds data and store in database"""
    for event_data in odds_data:
        try:
            # Check if event already exists
            existing_event = OddsEvent.query.filter_by(id=event_data['id']).first()
            
            if existing_event:
                # Store current odds as historical data before updating
                if existing_event.bookmakers:
                    historical_odds = HistoricalOdds(
                        event_id=existing_event.uuid,
                        bookmakers=existing_event.bookmakers,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.session.add(historical_odds)
                
                # Update existing event
                existing_event.bookmakers = event_data['bookmakers']
                existing_event.updated_at = datetime.now(timezone.utc)
            else:
                # Create new event
                new_event = OddsEvent(
                    uuid=str(uuid.uuid4()),
                    id=event_data['id'],
                    sport_key=event_data['sport_key'],
                    sport_title=event_data['sport_title'],
                    commence_time=datetime.fromisoformat(event_data['commence_time'].replace('Z', '+00:00')),
                    home_team=event_data['home_team'],
                    away_team=event_data['away_team'],
                    bookmakers=event_data['bookmakers']
                )
                db.session.add(new_event)
                db.session.flush()  # Get the UUID for historical odds
                
                # Store initial odds as historical data
                historical_odds = HistoricalOdds(
                    event_id=new_event.uuid,
                    bookmakers=event_data['bookmakers'],
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(historical_odds)
        
        except Exception as e:
            print(f"Error processing event {event_data.get('id', 'unknown')}: {str(e)}")
            db.session.rollback()
            continue
    
    db.session.commit()
    print("Successfully processed NBA odds")

def fetch_scores(db):
    """Fetch and store scores data from the API"""
    from app.models import OddsEvent, Score

    url = f"{BASE_URL}/sports/basketball_nba/scores"
    params = {
        "daysFrom": 1,
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 401:
            print("[INFO] API key invalid. Using mock scores.")
            generate_mock_scores(db)
            return
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("[INFO] No scores data returned from API. Using mock scores.")
            generate_mock_scores(db)
            return

        print(f"[INFO] Fetched {len(data)} scores")

        for score_data in data:
            try:
                # Find the corresponding odds event
                odds_event = OddsEvent.query.filter_by(id=score_data["id"]).first()
                
                if not odds_event:
                    print(f"[WARN] No matching odds event found for score {score_data['id']}")
                    continue

                # Check if score already exists
                existing_score = Score.query.filter_by(
                    event_id=odds_event.uuid
                ).first()

                if existing_score:
                    # Update existing score
                    existing_score.completed = score_data["completed"]
                    existing_score.scores = score_data["scores"]
                    print(f"[INFO] Updated existing Score for event: {odds_event.uuid}")
                else:
                    # Create new score
                    new_score = Score(
                        event_id=odds_event.uuid,
                        completed=score_data["completed"],
                        commence_time=datetime.strptime(score_data["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                        home_team=score_data["home_team"],
                        away_team=score_data["away_team"],
                        scores=score_data["scores"]
                    )
                    db.session.add(new_score)
                    print(f"[INFO] Created new Score for event: {odds_event.uuid}")

            except Exception as e:
                print(f"[ERROR] Failed to process score {score_data.get('id', 'unknown')}: {e}")
                db.session.rollback()

        db.session.commit()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch scores data: {e}")
        print("[INFO] Using mock scores instead.")
        generate_mock_scores(db)
    except Exception as e:
        print(f"[ERROR] Unexpected error in fetch_scores: {e}")
        print("[INFO] Using mock scores instead.")
        generate_mock_scores(db)
        db.session.rollback()

def generate_mock_scores(db):
    """Generate mock scores for testing when API is unavailable"""
    from app.models import OddsEvent, Score
    from datetime import datetime, timezone
    
    # Get all events without scores
    events = OddsEvent.query.all()
    
    for event in events:
        # Skip if score already exists
        if Score.query.filter_by(event_id=event.uuid).first():
            continue
            
        # Create mock score
        mock_score = Score(
            event_id=event.uuid,
            completed=False,
            commence_time=event.commence_time,
            home_team=event.home_team,
            away_team=event.away_team,
            scores={
                'home': 0,
                'away': 0
            }
        )
        db.session.add(mock_score)
    
    try:
        db.session.commit()
        print("[INFO] Generated mock scores for all events")
    except Exception as e:
        print(f"[ERROR] Failed to generate mock scores: {e}")
        db.session.rollback()

def fetch_all_data(db):
    """Fetch both odds and scores data"""
    print("[INFO] Starting data fetch...")
    fetch_odds()
    fetch_scores(db)
    print("[INFO] Data fetch completed")
