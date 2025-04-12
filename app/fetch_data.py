import requests
import os
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")

import requests
import os
from datetime import datetime
from app import db
from app.models import OddsEvent  # Adjust according to your model

API_KEY = os.getenv("ODDS_API_KEY")

# app/fetch_data.py
def fetch_odds(db):
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
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

    # Loop through the events in the data
    for event in data:
        try:
            odds_event = OddsEvent(
                id=event['id'],
                sport_key=event['sport_key'],
                sport_title=event['sport_title'],
                commence_time=datetime.strptime(event['commence_time'], "%Y-%m-%dT%H:%M:%SZ"),
                home_team=event['home_team'],
                away_team=event['away_team'],
                bookmakers=event['bookmakers']  # Full JSON response for bookmakers
            )
            db.session.add(odds_event)
            db.session.commit()
            print(f"[INFO] Inserted OddsEvent: {event['id']}")

            if 'score' in event:
                score = Score(
                    event_id=event['id'],
                    completed=event['score']['completed'],
                    commence_time=datetime.strptime(event['commence_time'], "%Y-%m-%dT%H:%M:%SZ"),
                    home_team=event['home_team'],
                    away_team=event['away_team'],
                    scores=event['score']['scores']
                )
                db.session.add(score)
                db.session.commit()
                print(f"[INFO] Inserted Score for Event: {event['id']}")
        
        except Exception as e:
            print(f"[ERROR] Failed to insert event {event['id']}: {e}")

                db.session.commit()
                print(f"[INFO] Inserted Score for Event: {event['id']}")
        
        except Exception as e:
            print(f"[ERROR] Failed to insert event {event['id']}: {e}")
