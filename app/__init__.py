from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Load the configuration from config.py
    app.config.from_object(Config)
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Import the main Blueprint after the app is created to avoid circular imports
    from app.routes import main  # Correct import based on where your Blueprint is defined
    app.register_blueprint(main)  # Register the Blueprint

    return app


