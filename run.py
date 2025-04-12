from app import create_app
from apscheduler.schedulers.background import BackgroundScheduler
from app.fetch_data import fetch_odds
from app import db

app = create_app()

# Move the scheduler outside the __main__ block so it runs on Render
scheduler = BackgroundScheduler(daemon=True)

def scheduled_job():
    with app.app_context():
        print("[INFO] Scheduled job running...")
        try:
            fetch_odds(db)
            print("[INFO] Scheduled job completed")
        except Exception as e:
            print(f"[ERROR] Scheduled job failed: {e}")

scheduler.add_job(func=scheduled_job, trigger="interval", minutes=10)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)

