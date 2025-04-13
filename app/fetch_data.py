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
            event_uuid = event["id"]  # Use the event id from the API as the UUID (no need to generate a new one)

            # Always insert new OddsEvent, bypassing update
            odds_event = OddsEvent(
                uuid=event_uuid,  # Use the event UUID from the API
                id=event_uuid,  # Store the API's event_id
                sport_key=event["sport_key"],
                sport_title=event["sport_title"],
                commence_time=datetime.strptime(event["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                home_team=event["home_team"],
                away_team=event["away_team"],
                bookmakers=event["bookmakers"],
            )
            db.session.add(odds_event)
            print(f"[INFO] Inserted new OddsEvent: {event_uuid}")
            db.session.commit()

            # Handle score data (if any)
            if "score" in event:
                score_data = event["score"]
                # Insert new score even if it already exists (no check for duplicates)
                score = Score(
                    event_id=event_uuid,  # Link score to OddsEvent by event UUID
                    completed=score_data["completed"],
                    commence_time=datetime.strptime(event["commence_time"], "%Y-%m-%dT%H:%M:%SZ"),
                    home_team=event["home_team"],
                    away_team=event["away_team"],
                    scores=score_data["scores"]
                )
                db.session.add(score)
                db.session.commit()
                print(f"[INFO] Inserted new Score for Event: {event_uuid}")

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"[ERROR] Database error for event {event_uuid}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to process event {event.get('id', 'unknown')}: {e}")

