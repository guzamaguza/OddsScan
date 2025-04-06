from app import create_app
import requests
import psycopg2
import pandas as pd
from datetime import datetime
# Create the app instance
app = create_app()


API_KEY = 'ODDS_API_KEY'  # Replace with your Odds API key
SPORT = 'basketball_nba'
REGION = 'us'
MARKETS = 'h2h,spreads,totals'
API_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal'

def fetch_and_store_odds():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
        else:
            print(f"Error fetching data from API: {response.status_code}")
            return

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="your-db-host",  # e.g., "your-db-host.render.com"
            dbname="your-db-name",
            user="your-db-user",
            password="your-db-password",
            port="5432"
        )
        cursor = conn.cursor()

        rows = []
        for event in data:
            event_id = event.get('id', 'N/A')
            home_team = event.get('home_team', 'N/A')
            away_team = event.get('away_team', 'N/A')
            commence_time = pd.to_datetime(event.get('commence_time')).strftime('%Y-%m-%d %H:%M:%S')
            timestamp = datetime.now().isoformat()

            for bookmaker in event.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', 'N/A')
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key', 'N/A')
                    for outcome in market.get('outcomes', []):
                        rows.append((
                            event_id, home_team, away_team, commence_time, bookmaker_name,
                            market_key, outcome.get('name', 'N/A'), outcome.get('price', 'N/A'),
                            outcome.get('point', 'N/A'), timestamp, 'pre_event'
                        ))

        if rows:
            insert_query = '''
                INSERT INTO odds (event_id, home_team, away_team, commence_time, bookmaker, market, outcome, price, point, timestamp, odds_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.executemany(insert_query, rows)
            conn.commit()

        cursor.close()
        conn.close()
    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching data from API: {req_err}")
    except psycopg2.Error as e:
        print(f"Error inserting data into PostgreSQL: {e}")

from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_odds, 'interval', minutes=60)  # Fetch data every hour
    scheduler.start()

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
