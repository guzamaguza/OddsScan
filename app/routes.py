from flask import Blueprint, render_template, current_app
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from flask import render_template
from app import create_app
from app import db 
from flask import Blueprint, render_template


from flask import Blueprint, render_template
from app import db
from app.models import Odds  # Ensure you have this import to query the database

# Create a Blueprint for the routes
main = Blueprint('main', __name__)

# Route for the homepage
@main.route('/')
def home():
    # Fetch all matches from the database
    matches = Odds.query.all()  # Fetch all odds/matches from the database
    return render_template('index.html', matches=matches)

# Route for individual match details
@main.route('/match/<event_id>')
def match_details(event_id):
    # Fetch match details based on event_id
    match = Odds.query.filter_by(event_id=event_id).first()  # Query match by event_id
    if match:
        return render_template('match_details.html', match=match)
    else:
        return "Match not found", 404  # Return 404 if match not found


