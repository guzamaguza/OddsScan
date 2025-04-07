from app import create_app
import requests
import psycopg2
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Create the app instance
app = create_app()

# Load environment variables from .env
load_dotenv()

# Get the environment variables for the API and Database URL
API_KEY = os.getenv('ODDS_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

SPORT = 'basketball_nba'
REGION = 'us'
MARKETS = 'h2h,spreads,totals'
API_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'

def fetch_and_store_odds(url, odds_type):
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception for non-2xx status codes
        print("RAW API Response:", response.text)
        print("Status Code:", response.status_code)
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
                        rows.append((event_id, home_team, away_team, commence_time, bookmaker_name,
                                     market_key, outcome.get('name', 'N/A'), outcome.get('price', 'N/A'),
                                     outcome.get('point', 'N/A'), timestamp, odds_type))

        # Debug: Print rows to check if we have any data to insert
        print(f"Rows to insert: {rows}")

        if rows:
            # Connect to PostgreSQL using the DATABASE_URL
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()

            # Insert the rows into PostgreSQL
            insert_query = '''
                INSERT INTO odds (event_id, home_team, away_team, commence_time, bookmaker, market, outcome, price, point, timestamp, odds_type)
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
        print(f"PostgreSQL error: {e.pgerror}, details: {e.diag.message_primary}")



def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: fetch_and_store_odds(API_URL, SPORT), 'interval', minutes=30)
    scheduler.start()
    print("Scheduler started!")  # Debug print



# --- Add this block to run on startup ---
print("[DEBUG] Running fetch_and_store_odds manually on startup...")
fetch_and_store_odds(API_URL, SPORT)

if __name__ == "__main__":
    app.run(debug=True)

