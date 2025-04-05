from flask import Blueprint, render_template, current_app
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from app import db
from app.odds import fetch_and_store_odds  # Import the function correctly

# Define the Blueprint
main = Blueprint('main', __name__)

from flask import Blueprint, render_template
from app.odds import fetch_events, plot_odds  # Import functions from odds.py

# Define the Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Fetch events from the database using the fetch_events function
    events = fetch_events()

    # Pass the events to the template
    return render_template("index.html", events=events)

# Route to show odds plot
@main.route('/plot/<event_id>')
def show_plot(event_id):
    # Generate the odds plot using the plot_odds function
    img_base64 = plot_odds(event_id)
    
    # If a plot is returned, show it; otherwise, show a message
    if img_base64:
        return render_template('plot.html', img_data=img_base64)
    else:
        return "No data found for the selected match."



