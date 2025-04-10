import requests
import psycopg2
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('ODDS_API_KEY')
SPORT = 'basketball_nba'
REGION = 'us'
MARKETS = 'h2h,spreads,totals'

ODDS_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'
SCORES_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/scores/?daysFrom=1&apiKey={API_KEY}'

def fetch_and_store_odds(url, odds_type):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

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
                # Create a valid JSON structure for 'bookmakers'
                bookmaker_data = [{'title': bookmaker.get('title', 'N/A'), 'key': bookmaker.get('key', 'N/A')}]
                
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key', 'N/A')
                    for outcome in market.get('outcomes', []):
                        price = outcome.get('price', None)
                        point = outcome.get('point', None)

                        rows.append((
                            event_id, home_team, away_team, commence_time,
                            bookmaker_data,  # Now passing valid JSON
                            market_key, outcome.get('name', 'N/A'), price, point,
                            timestamp, odds_type
                        ))

        if rows:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()

            insert_query = '''
                INSERT INTO odds (event_id, home_team, away_team, commence_time, bookmakers, market, outcome, price, point, timestamp, odds_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_id, commence_time) DO NOTHING
            '''

            inserted_count = 0
            for row in rows:
                cursor.execute(insert_query, row)
                inserted_count += 1

            conn.commit()
            cursor.close()
            conn.close()

            print(f"{inserted_count} new {odds_type} odds rows inserted.")
        else:
            print(f"No {odds_type} odds to insert.")
    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching {odds_type} data: {req_err}")
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e.pgerror}, details: {e.diag.message_primary}")

def fetch_and_store_scores():
    try:
        response = requests.get(SCORES_URL)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("No score data returned from the API.")
            return

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        updated_count = 0
        for event in data:
            if not event.get("scores"):
                continue

            event_id = event["id"]
            completed = event.get("completed", False)
            home_team = event.get("home_team")
            away_team = event.get("away_team")

            try:
                scores = {s["name"]: int(s["score"]) for s in event["scores"]}
                home_score = scores[home_team]
                away_score = scores[away_team]
            except KeyError:
                print(f"[WARN] Missing score for {home_team} or {away_team} in event {event_id}, skipping.")
                continue

            now = datetime.utcnow().isoformat()

            # UPSERT into scores table
            cursor.execute("""
                INSERT INTO scores (event_id, home_score, away_score, completed, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (event_id) DO UPDATE SET
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    completed = EXCLUDED.completed,
                    last_updated = EXCLUDED.last_updated
            """, (event_id, home_score, away_score, completed, now))
            updated_count += cursor.rowcount

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {updated_count} events updated in scores table.")
    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching scores: {req_err}")
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e.pgerror}, details: {e.diag.message_primary}")


# Start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: fetch_and_store_odds(ODDS_URL, SPORT), 'interval', minutes=30)
    scheduler.add_job(fetch_and_store_scores, 'interval', minutes=30)
    scheduler.start()
    print("🕒 Scheduler started!")

