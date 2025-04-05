from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Apply the configuration

    db.init_app(app)  # Initialize SQLAlchemy with the app
    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app and db

    # Register Blueprints (or routes)
    from app.routes import main
    app.register_blueprint(main)

    return app


