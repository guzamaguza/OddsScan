from flask import Blueprint, render_template, current_app
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from flask import render_template
from app import create_app
from app import db 
from flask import Blueprint, render_template


# Create a Blueprint for your routes
main = Blueprint('main', __name__)

# Route to home page
@main.route('/')
def home():
    return render_template('index.html')

# Route for individual match details
@app.route('/match/<event_id>')
def match_details(event_id):
    # Fetch match details based on event_id
    match = Odds.query.filter_by(event_id=event_id).first()  # Query match by event_id
    if match:
        return render_template('match_details.html', match=match)
    else:
        return "Match not found", 404  # Return 404 if match not found


