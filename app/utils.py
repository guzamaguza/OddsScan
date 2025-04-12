import requests
import os

API_KEY = os.getenv('ODDS_API_KEY')
BASE_URL = "https://api.the-odds-api.com/v4"

def get_sports():
    url = f"{BASE_URL}/sports/?apiKey={API_KEY}"
    return requests.get(url).json()

def get_odds(sport_key):
    url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=american"
    return requests.get(url).json()


