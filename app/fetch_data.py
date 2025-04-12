import requests
import os
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")

def fetch_odds():
    from app import db
    from app.models import OddsEvent  # And Score if needed
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

        print(f"[INFO] Inserted {len(data)} events.")
