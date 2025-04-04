from flask import Blueprint, render_template
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from app import db

# Define the Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Fetch events from the database
    conn = sqlite3.connect('odds.db')
    query = "SELECT DISTINCT event_id, home_team, away_team, start_time FROM odds"
    events = pd.read_sql_query(query, conn)
    conn.close()

    # Convert start_time to a readable format
    events['start_time'] = pd.to_datetime(events['start_time']).dt.strftime('%Y-%m-%d %H:%M')

    # Pass the events as a list of dictionaries
    return render_template("index.html", events=events.to_dict(orient='records'))


# Route to show odds plot
@main.route('/plot/<event_id>')
def show_plot(event_id):
    img_base64 = plot_odds(event_id)  # Function that generates the plot
    if img_base64:
        return render_template('plot.html', img_data=img_base64)
    else:
        return "No data found for the selected match."

# Function to generate and return plot as base64
def plot_odds(event_id):
    conn = sqlite3.connect('odds.db')
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
    
    # Plotting the odds over time
    plt.figure(figsize=(12, 6))
    for bookmaker in df['bookmaker'].unique():
        subset = df[(df['outcome'] == home_team) & (df['bookmaker'] == bookmaker)]
        plt.plot(subset['timestamp'], subset['price'], marker='o', label=f"{bookmaker} (Home)")

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


@main.route("/init-db")
def init_db():
    # Your initialization logic here
    db.create_all()
    return "Database initialized"


@main.route("/test-db")
def test_db():
    try:
        result = db.session.execute("SELECT 1")
        return {"status": "success", "message": "Database connection successful", "result": result.fetchone()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

