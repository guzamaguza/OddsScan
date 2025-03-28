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

# Route to show odds plot
@main.route('/plot/<event_id>')
def show_plot(event_id):
    img_base64 = plot_odds(event_id)  # Function that generates the plot
    if img_base64:
        return render_template('plot.html', img_data=img_base64)
    else:
        return "No data found for the selected match."
