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



# Function to fetch events from the database
def fetch_events():
    # Connect to the database
    conn = sqlite3.connect('odds.db')
    query = "SELECT DISTINCT event_id, home_team, away_team, start_time FROM odds"
    events = pd.read_sql_query(query, conn)
    conn.close()

    # Convert start_time to a readable format
    events['start_time'] = pd.to_datetime(events['start_time']).dt.strftime('%Y-%m-%d %H:%M')

    # Return events as a list of dictionaries
    return events.to_dict(orient='records')

# Function to generate and return odds plot as base64
def plot_odds(event_id):
    # Connect to the database
    conn = sqlite3.connect('odds.db')
    query = """
        SELECT home_team, away_team, start_time, outcome, price, bookmaker, timestamp
        FROM odds 
        WHERE event_id = ?
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(event_id,))
    conn.close()

    # If no data is found, return None
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



