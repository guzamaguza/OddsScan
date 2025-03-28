from flask import Blueprint, render_template
import sqlite3
import pandas as pd

# Define the Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Fetch events from the database
    conn = sqlite3.connect('odds.db')
    query = "SELECT DISTINCT event_id, home_team, away_team FROM odds"
    events = pd.read_sql_query(query, conn).to_dict(orient='records')
    conn.close()

    # Pass the events to the template
    return render_template("index.html", events=events)
