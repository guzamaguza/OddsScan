import requests
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import uuid
from flask import current_app
from app.models import OddsEvent, Score, HistoricalOdds

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"

def fetch_odds(db):
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
        
        if response.status_code != 200:
            print("Error fetching NBA odds:", response.text)
            return
            
        odds_data = response.json()
        print(f"Fetched {len(odds_data)} NBA events")
        
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
        
    except Exception as e:
        print("Error processing NBA odds:", str(e))
        db.session.rollback()

def fetch_scores(db):
    """Fetch and store scores data from the API"""
    url = f"{BASE_URL}/sports/basketball_nba/scores"
    params = {
        "daysFrom": 1,
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("[INFO] No scores data returned from API")
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
    except Exception as e:
        print(f"[ERROR] Unexpected error in fetch_scores: {e}")
        db.session.rollback()

def fetch_all_data(db):
    """Fetch both odds and scores data"""
    print("[INFO] Starting data fetch...")
    fetch_odds(db)
    fetch_scores(db)
    print("[INFO] Data fetch completed")
