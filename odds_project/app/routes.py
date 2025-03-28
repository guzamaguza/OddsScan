from flask import Blueprint, render_template

# Define the Blueprint without importing `app`
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template("index.html")
