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

def fetch_odds():
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
    
    # Assuming you have a model called OddsEvent, for example:
    for event in data:
        try:
            odds_event = OddsEvent(
                event_id=event['id'],  # Adjust according to your data structure
                home_team=event['home_team'],
                away_team=event['away_team'],
                odds=event['odds'],
                timestamp=datetime.now()
            )
            db.session.add(odds_event)
            db.session.commit()
            print(f"[INFO] Inserted event: {event['id']}")
        except Exception as e:
            print(f"[ERROR] Failed to insert event: {e}")


    data = response.json()

    with db.session.begin():  # Ensures that the session is committed at the end
        for item in data:
            event = OddsEvent.query.get(item["id"])
            if not event:  # If the event doesn't exist, create a new one
                event = OddsEvent(
                    id=item["id"],
                    sport_key=item["sport_key"],
                    sport_title=item["sport_title"],
                    commence_time=datetime.fromisoformat(item["commence_time"]),
                    home_team=item["home_team"],
                    away_team=item["away_team"],
                    bookmakers=item["bookmakers"],
                )
                db.session.add(event)

        db.session.commit()  # Commit all the changes
        print(f"[INFO] Inserted {len(data)} events.")
