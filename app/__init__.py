from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import the main Blueprint after the app is created to avoid circular imports
    from app.routes import main  # Correct import based on where your Blueprint is defined
    app.register_blueprint(main)  # Register the Blueprint

    return app

