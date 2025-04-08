from flask import Blueprint, render_template
from app import db
from sqlalchemy import text
from app.models import Odds, Score  # Ensure you have this import to query the database

# Create a Blueprint for the routes
main = Blueprint('main', __name__)

# Route for the home page
@main.route('/')
def home():
    # Query the odds table for distinct NBA events, including completed and score information
    query = text("""
        SELECT DISTINCT ON (odds.event_id) odds.event_id, odds.home_team, odds.away_team, odds.commence_time,
            odds.completed, score.home_score, score.away_score
        FROM odds
        LEFT JOIN score ON odds.event_id = score.event_id
        ORDER BY odds.event_id, odds.commence_time DESC
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
            'commence_time': event[3],
            'completed': event[4],
            'home_score': event[5] if event[5] is not None else "N/A",  # Handle missing scores
            'away_score': event[6] if event[6] is not None else "N/A"   # Handle missing scores
        }
        for event in events
    ]

    return render_template('index.html', matches=events_list)

# Route for individual match details
@main.route('/match/<event_id>')
def match_details(event_id):
    # Fetch match details based on event_id, including completed status and scores
    match = db.session.query(Odds, Score).outerjoin(Score, Odds.event_id == Score.event_id).filter(Odds.event_id == event_id).first()

    if match:
        odds, score = match
        # Ensure you pass the newly added attributes to the template
        match_data = {
            'event_id': odds.event_id,
            'home_team': odds.home_team,
            'away_team': odds.away_team,
            'commence_time': odds.commence_time,
            'bookmaker': odds.bookmaker,
            'market': odds.market,
            'outcome': odds.outcome,
            'price': odds.price,
            'point': odds.point,
            'timestamp': odds.timestamp,
            'odds_type': odds.odds_type,
            'completed': score.completed if score else False,
            'home_score': score.home_score if score else "N/A",  # Handle missing scores
            'away_score': score.away_score if score else "N/A"   # Handle missing scores
        }
        return render_template('match_details.html', match=match_data)
    else:
        return "Match not found", 404  # Return 404 if match not found

