from app import create_app, db
from app.models import Sport, OddsEvent
from app.utils import get_sports, get_odds
from datetime import datetime

app = create_app()

with app.app_context():
    sports = get_sports()
    for sport in sports:
        db.session.merge(Sport(
            id=sport['key'],
            key=sport['key'],
            group=sport['group'],
            title=sport['title'],
            active=sport['active'],
            has_outrights=sport['has_outrights']
        ))
    db.session.commit()

    for sport in sports:
        if sport['active']:
            odds = get_odds(sport['key'])
            for event in odds:
                db.session.merge(OddsEvent(
                    id=event['id'],
                    sport_key=event['sport_key'],
                    sport_title=event['sport_title'],
                    commence_time=datetime.fromisoformat(event['commence_time'].replace("Z", "+00:00")),
                    home_team=event['home_team'],
                    away_team=event['away_team'],
                    bookmakers=event['bookmakers']
                ))
    db.session.commit()

