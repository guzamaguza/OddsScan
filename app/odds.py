import requests
import pandas as pd
import certifi
from flask import Flask, render_template, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Odds, Event  # Make sure to import Event

# Flask App Initialization
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Initialize PostgreSQL

# Fetch and Store Odds in PostgreSQL
def fetch_and_store_odds(url, odds_type):
    try:
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()
        data = response.json()

        if not data:
            print(f"No {odds_type} data returned from API.")
            return False

        rows = []
        for event in data:
            event_id = event.get('id', 'N/A')
            home_team = event.get('home_team', 'N/A')
            away_team = event.get('away_team', 'N/A')
            commence_time = event.get('commence_time', 'N/A')
            timestamp = pd.Timestamp.now().isoformat()

            # Check if the event already exists in the database, if not, create a new Event
            existing_event = Event.query.filter_by(id=event_id).first()
            if not existing_event:
                existing_event = Event(id=event_id, name=f'{home_team} vs {away_team}')
                db.session.add(existing_event)
                db.session.commit()  # Commit to get the event ID in DB

            for bookmaker in event.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', 'N/A')
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key', 'N/A')
                    for outcome in market.get('outcomes', []):
                        rows.append(Odds(
                            event_id=event_id,
                            time=commence_time,
                            odds_value=float(outcome.get('price', 0))
                        ))

        with app.app_context():
            db.session.bulk_save_objects(rows)
            db.session.commit()
            print(f"{odds_type} odds data successfully stored.")
        return True

    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching {odds_type} data: {req_err}")
        return False


# Flask Routes
@app.route('/init-db')
def init_db():
    """Initialize the database tables."""
    with app.app_context():
        db.create_all()
        return "Database tables created successfully."


@app.route('/fetch_odds')
def fetch_odds():
    """Fetch and store odds."""
    API_KEY = app.config['ODDS_API_KEY']
    SPORT = 'basketball_nba'
    REGION = 'us'
    MARKETS = 'h2h,spreads,totals'
    
    PRE_EVENT_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal'
    LIVE_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'

    pre_event_updated = fetch_and_store_odds(PRE_EVENT_URL, "Pre-event")
    live_updated = fetch_and_store_odds(LIVE_URL, "Live")

    return {"pre_event_updated": pre_event_updated, "live_updated": live_updated}


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
