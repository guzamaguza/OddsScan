from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config  # Correct the import path


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Apply the configuration

    db.init_app(app)  # Initialize SQLAlchemy with the app

    # Register Blueprints (or routes)
    from app.routes import main
    app.register_blueprint(main)

    return app


