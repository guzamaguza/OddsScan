import requests
import os
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"

def fetch_odds(db):
    """Fetch and store odds data from the API"""
    from app.models import OddsEvent

    url = f"{BASE_URL}/sports/basketball_nba/odds"
    params = {
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "apiKey": API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("[INFO] No odds data returned from API")
            return

        print(f"[INFO] Fetched {len(data)} odds events")

        for event in data:
            try:
                # Check if event already exists
                existing_event = OddsEvent.query.filter_by(id=event["id"]).first()
                
                if existing_event:
                    # Update existing event
                    existing_event.bookmakers = event["bookmakers"]
                    print(f"[INFO] Updated existing OddsEvent: {existing_event.uuid}")
                else:
                    # Create new event
                    new_event = OddsEvent(
                        id=event["id"],
                        sport_key=event["sport_key"],
                        sport_title=event["sport_title"],
                        commence_time=datetime.strptime(event["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                        home_team=event["home_team"],
                        away_team=event["away_team"],
                        bookmakers=event["bookmakers"]
                    )
                    db.session.add(new_event)
                    print(f"[INFO] Created new OddsEvent: {new_event.uuid}")

            except Exception as e:
                print(f"[ERROR] Failed to process odds event {event.get('id', 'unknown')}: {e}")
                db.session.rollback()

        db.session.commit()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch odds data: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in fetch_odds: {e}")
        db.session.rollback()

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
