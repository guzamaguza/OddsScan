from flask import Blueprint, render_template
from app import db
from sqlalchemy import text  # Import text() to handle raw SQL queries
from app.models import Odds  # Ensure you have this import to query the database

# Create a Blueprint for the routes
main = Blueprint('main', __name__)

from sqlalchemy import text

@main.route('/')
def home():
    # Query the odds table for distinct NBA events
    query = text("""
        SELECT DISTINCT ON (event_id) event_id, home_team, away_team, commence_time
        FROM odds
        ORDER BY event_id, commence_time DESC
    """)
    events = db.session.execute(query).fetchall()

    # Debugging: Print the fetched events
    print(f"Fetched distinct events: {events}")

    if not events:
        print("No events found in the database.")

    # Convert the query results into a list of dictionaries
    events_list = [
        {
            'event_id': event[0],
            'home_team': event[1],
            'away_team': event[2],
            'commence_time': event[3]
        }
        for event in events
    ]

    return render_template('index.html', matches=events_list)


# Route for individual match details
@main.route('/match/<event_id>')
def match_details(event_id):
    # Fetch match details based on event_id
    match = Odds.query.filter_by(event_id=event_id).first()  # Query match by event_id
    if match:
        return render_template('match_details.html', match=match)
    else:
        return "Match not found", 404  # Return 404 if match not found

