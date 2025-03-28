from flask import Blueprint, render_template

# Define the blueprint
main = Blueprint('main', __name__)

# Define your routes
@main.route('/')
def home():
    return render_template("index.html")
