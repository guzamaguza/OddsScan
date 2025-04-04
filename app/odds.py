import requests
import pandas as pd
import sqlite3
import certifi
import ssl
import time
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template, request, jsonify
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Flask App Initialization
app = Flask(__name__)

app.config.from_object(Config)  # Load settings from config.py

db = SQLAlchemy(app)  # Initialize database


# Constants
API_KEY = '8781b066fc9a11b5d2c6eb6a16d7af43'  # Replace with your Odds API key
SPORT = 'basketball_nba'  # NBA Basketball
REGION = 'us'  # Region for odds (e.g., 'us', 'uk', 'eu')
MARKETS = 'h2h,spreads,totals'  # Market types for both pre-game and live odds
DB_NAME = 'odds.db'

PRE_EVENT_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal'
LIVE_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'


# Create Database
def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT,
            home_team TEXT,
            away_team TEXT,
            start_time TEXT,
            bookmaker TEXT,
            market TEXT,
            outcome TEXT,
            price REAL,
            point REAL,
            timestamp TEXT,
            odds_type TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Fetch and Store Odds
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

            for bookmaker in event.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', 'N/A')
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key', 'N/A')
                    for outcome in market.get('outcomes', []):
                        rows.append((event_id, home_team, away_team, commence_time, bookmaker_name,
                                     market_key, outcome.get('name', 'N/A'), outcome.get('price', 'N/A'),
                                     outcome.get('point', 'N/A'), timestamp, odds_type))

        if rows:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO odds (event_id, home_team, away_team, start_time, bookmaker, market, outcome, price, point, timestamp, odds_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows)
            conn.commit()
            conn.close()
            print(f"{odds_type} odds data successfully stored.")
            return True

        return False

    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching {odds_type} data: {req_err}")
        return False

# Function to Plot Odds and Return as Image URL
def plot_odds(event_id):
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT home_team, away_team, start_time, outcome, price, bookmaker, timestamp
        FROM odds 
        WHERE event_id = ?
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(event_id,))
    conn.close()

    if df.empty:
        return None

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['start_time'] = pd.to_datetime(df['start_time'])
    event_start_time = df['start_time'].iloc[0]

    home_team = df['home_team'].iloc[0]
    away_team = df['away_team'].iloc[0]

    plt.figure(figsize=(12, 6))

    # Plot odds for the home team
    for bookmaker in df['bookmaker'].unique():
        subset_home = df[(df['outcome'] == home_team) & (df['bookmaker'] == bookmaker)]
        if not subset_home.empty:
            plt.plot(subset_home['timestamp'], subset_home['price'], marker='o', label=f"{bookmaker} (Home)")

        subset_away = df[(df['outcome'] == away_team) & (df['bookmaker'] == bookmaker)]
        if not subset_away.empty:
            plt.plot(subset_away['timestamp'], subset_away['price'], marker='s', linestyle='dashed', label=f"{bookmaker} (Away)")

    plt.axvline(event_start_time, color='r', linestyle='--', label='Event Start Time')
    plt.xlabel('Time')
    plt.ylabel('Odds')
    plt.title(f"Odds Over Time: {home_team} vs {away_team}")
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


# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fetch_odds')
def fetch_odds():
    pre_event_updated = fetch_and_store_odds(PRE_EVENT_URL, "Pre-event")
    live_updated = fetch_and_store_odds(LIVE_URL, "Live")

    no_new_data = not (pre_event_updated or live_updated)  # True if no new data added

    # Fetch events again for display
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT DISTINCT event_id, home_team, away_team, start_time FROM odds"
    events = pd.read_sql_query(query, conn).to_dict(orient='records')
    conn.close()

    return render_template("index.html", events=events, no_new_data=no_new_data)



@app.route('/plot/<event_id>')
def show_plot(event_id):
    img_base64 = plot_odds(event_id)
    if img_base64:
        return render_template('plot.html', img_data=img_base64)
    else:
        return "No data found for the selected match."


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Test the connection
with app.app_context():
    try:
        result = db.session.execute("SELECT 1")
        print("✅ Database connection successful:", result.fetchone())
    except Exception as e:
        print("❌ Database connection failed:", str(e))



# Run Flask App
if __name__ == '__main__':
    create_database()
    app.run(debug=True)
