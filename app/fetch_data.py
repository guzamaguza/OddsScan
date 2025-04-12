import requests
import os
from app.models import OddsEvent  # And Score if needed
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")

def fetch_odds():
    from app import db
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
    params = {
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("[ERROR]", response.json())
        return

    data = response.json()

    with app.app_context():
        for item in data:
            event = OddsEvent.query.get(item["id"])
            if not event:
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
        db.session.commit()
        print(f"[INFO] Inserted {len(data)} events.")
