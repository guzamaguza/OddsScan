from app import create_app
import os
from dotenv import load_dotenv
from app.utils import start_scheduler

# Create the app instance
app = create_app()

# Load environment variables from .env
load_dotenv()

# Start the scheduler
start_scheduler()

if __name__ == "__main__":
    app.run(debug=True)
