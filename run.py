from app import create_app
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Create the app instance
app = create_app()

# Load environment variables from .env
load_dotenv()

# Define your API endpoint details
API_KEY = os.getenv('ODDS_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
SPORT = 'basketball_nba'
REGION = 'us'
MARKETS = 'h2h,spreads,totals'

ODDS_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal&eventStatus=live'
SCORES_URL = f'https://api.the-odds-api.com/v4/sports/{SPORT}/scores/?daysFrom=1&apiKey={API_KEY}'

# Start the scheduler
def start_scheduler():
    from app.utils import fetch_and_store_odds, fetch_and_store_scores

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: fetch_and_store_odds(ODDS_URL, SPORT), 'interval', minutes=30)
    scheduler.add_job(fetch_and_store_scores, 'interval', minutes=30)
    scheduler.start()
    print("🕒 Scheduler started!")

if __name__ == "__main__":
    # The fetch_and_store_odds and fetch_and_store_scores are now managed in utils.py
    start_scheduler()
    app.run(debug=True)

