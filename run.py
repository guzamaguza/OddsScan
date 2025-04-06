import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models import Odds
import requests
import certifi
import ssl
import pandas as pd
import psycopg2
from psycopg2 import sql

# Setup SSL for secure connections
print(ssl.get_default_verify_paths())

# Constants
API_KEY = '8781b066fc9a11b5d2c6eb6a16d7af43'  # Replace with your Odds API key
SPORT = 'basketball_nba'  # NBA Basketball
REGION = 'us'  # Region for odds (e.g., 'us', 'uk', 'eu')
MARKETS = 'h2h,spreads,totals'  # Market types for both pre-game and live odds
PRE_EVENT_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal'
LIVE_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Function to fetch and store odds in the database
def fetch_and_store_odds(url, odds_type):
    try:
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()
        data = response.json()

        # Debug: Print API Response to ensure we are getting data
        print(f"API Response: {data}")

        if not data:
            print(f"No {odds_type} data returned from API.")
            return

        rows = []
        for event in data:
            event_id = event.get('id', 'N/A')
            home_team = event.get('home_team', 'N/A')
            away_team = event.get('away_team', 'N/A')
            commence_time = event.get('commence_time', 'N/A')
            timestamp = pd.Timestamp.now().isoformat()

            for bookmaker in event.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', 'N/A')
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key', 'N/A')
                    for outcome in market.get('outcomes', []):
                        rows.append((
                            event_id, home_team, away_team, commence_time, bookmaker_name,
                            market_key, outcome.get('name', 'N/A'), outcome.get('price', 'N/A'),
                            outcome.get('point', 'N/A'), timestamp, odds_type
                        ))

        # Debug: Print rows to check if we have any data to insert
        print(f"Rows to insert: {rows}")

        if rows:
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host="your_host",  # e.g., "your-db-host.render.com"
                dbname="your_db_name",
                user="your_db_user",
                password="your_db_password",
                port="your_db_port"  # Typically 5432 for PostgreSQL
            )
            cursor = conn.cursor()

            # Insert the rows into PostgreSQL
            insert_query = '''
                INSERT INTO odds (event_id, home_team, away_team, start_time, bookmaker, market, outcome, price, point, timestamp, odds_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.executemany(insert_query, rows)
            conn.commit()
            cursor.close()
            conn.close()

            print(f"{odds_type} odds data successfully stored.")
        else:
            print(f"No {odds_type} odds to insert.")
    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching {odds_type} data: {req_err}")
    except psycopg2.Error as e:
        print(f"Error inserting data into PostgreSQL: {e}")