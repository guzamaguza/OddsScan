from flask import Flask
from your_blueprint_file import main  # Adjust the import path to your Blueprint file

def create_app():
    app = Flask(__name__)

    # Now we import the main blueprint AFTER app is created to avoid circular imports
    from app.routes import main
    app.register_blueprint(main)

    return app


