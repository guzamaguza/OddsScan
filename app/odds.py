import requests
import pandas as pd
import certifi
from flask import Flask, render_template, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.models import db, Odds, Event  # Make sure to import Event
import requests
import logging
from flask import current_app
from app import db
from app.models import Event, Odds  # Make sure you import your models properly
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from app import db

# Flask App Initialization
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  # Initialize PostgreSQL


# Function to generate and return odds plot as base64
def plot_odds(event_id):
    # Query data from PostgreSQL database using SQLAlchemy
    query = """
        SELECT home_team, away_team, start_time, outcome, price, bookmaker, timestamp
        FROM odds 
        WHERE event_id = :event_id
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, db.session.bind, params={'event_id': event_id})

    if df.empty:
        return None
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['start_time'] = pd.to_datetime(df['start_time'])
    event_start_time = df['start_time'].iloc[0]

    home_team = df['home_team'].iloc[0]
    away_team = df['away_team'].iloc[0]

    # Plotting the odds over time
    plt.figure(figsize=(12, 6))
    for bookmaker in df['bookmaker'].unique():
        subset = df[(df['outcome'] == home_team) & (df['bookmaker'] == bookmaker)]
        plt.plot(subset['timestamp'], subset['price'], marker='o', label=f"{bookmaker} (Home)")

    # Mark event start time on the plot
    plt.axvline(event_start_time, color='r', linestyle='--', label='Event Start Time')
    plt.xlabel('Time')
    plt.ylabel('Odds')
    plt.title(f"Home Team Odds Over Time: {home_team} vs {away_team}")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()

    # Save plot to buffer and encode as base64
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    plt.close()

    return img_base64

def fetch_and_store_odds(url, odds_type):
    try:
        # Log the URL to check if the request is being made
        logging.info(f"Fetching {odds_type} data from URL: {url}")
        
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()
        data = response.json()

        if not data:
            logging.error(f"No {odds_type} data returned from API.")
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

        with current_app.app_context():
            db.session.bulk_save_objects(rows)
            db.session.commit()
            logging.info(f"{odds_type} odds data successfully stored.")
        return True

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Error fetching {odds_type} data: {req_err}")
        return False



