import requests
import os
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

API_KEY = os.getenv("ODDS_API_KEY")

def fetch_odds(db):
    from app.models import OddsEvent, Score  # Avoid circular import issues

    url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("[ERROR] Unable to fetch data:", response.json())
        return

    data = response.json()
    if not data:
        print("[INFO] No data returned from API.")
        return

    print(f"[INFO] {len(data)} events fetched.")

    for event in data:
        try:
            event_uuid = str(uuid.uuid4())  # Generate a new UUID for the event if it's a new event

            # Check if the event already exists based on the event UUID
            odds_event = OddsEvent.query.filter_by(id=event_uuid).first()

            if not odds_event:
                # Insert new event
                odds_event = OddsEvent(
                    id=event_uuid,
                    sport_key=event["sport_key"],
                    sport_title=event["sport_title"],
                    commence_time=datetime.strptime(event["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                    home_team=event["home_team"],
                    away_team=event["away_team"],
                    bookmakers=event["bookmakers"],
                )
                db.session.add(odds_event)
                print(f"[INFO] Inserted new OddsEvent: {event_uuid}")
            else:
                # Update the existing bookmakers info
                odds_event.bookmakers = event["bookmakers"]
                odds_event.updated_at = datetime.utcnow()
                print(f"[INFO] Updated OddsEvent: {event_uuid}")

            db.session.commit()

            # Handle score data (if any)
            if "score" in event:
                score_data = event["score"]
                # Optional: prevent duplicate score inserts if you want
                existing_score = Score.query.filter_by(
                    event_id=event_uuid,
                    completed=score_data["completed"]
                ).first()

                if not existing_score:
                    score = Score(
                        event_id=event_uuid,
                        completed=score_data["completed"],
                        commence_time=datetime.strptime(event["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                        home_team=event["home_team"],
                        away_team=event["away_team"],
                        scores=score_data["scores"]
                    )
                    db.session.add(score)
                    db.session.commit()
                    print(f"[INFO] Inserted new Score for Event: {event_uuid}")
                else:
                    print(f"[INFO] Score for Event {event_uuid} already exists with same status.")

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"[ERROR] Database error for event {event_uuid}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to process event {event.get('id', 'unknown')}: {e}")
