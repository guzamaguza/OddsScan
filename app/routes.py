@main.route("/match/<uuid>/odds-history")
def odds_history(uuid):
    """Get historical odds data for a specific event"""
    from app.models import OddsEvent, HistoricalOdds
    from datetime import datetime, timezone

    print(f"\n[DEBUG] Fetching odds history for event: {uuid}")
    
    # Get the event
    event = OddsEvent.query.filter_by(uuid=uuid).first()
    if not event:
        print(f"[ERROR] Event {uuid} not found")
        return jsonify({"error": "Event not found"}), 404

    print(f"[DEBUG] Found event: {event.uuid}")
    print(f"- Home Team: {event.home_team}")
    print(f"- Away Team: {event.away_team}")

    # Get historical odds
    historical_odds = HistoricalOdds.query.filter_by(event_id=uuid).order_by(HistoricalOdds.created_at).all()
    print(f"[DEBUG] Found {len(historical_odds)} historical odds records")

    # Initialize chart data structure
    chart_data = {
        "labels": [],  # Timestamps
        "datasets": []  # List of datasets
    }

    # Process historical odds
    for history in historical_odds:
        if not history.bookmakers:
            continue
            
        timestamp = history.created_at.strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(timestamp)
        
        # Process each bookmaker's odds
        for bookmaker in history.bookmakers:
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        # Add to appropriate dataset
                        dataset_name = f"{bookmaker['key']} - {outcome['name']}"
                        dataset = next((d for d in chart_data["datasets"] if d["label"] == dataset_name), None)
                        
                        if not dataset:
                            dataset = {
                                "label": dataset_name,
                                "data": [],
                                "borderColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "backgroundColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "fill": False,
                                "tension": 0.1,
                                "pointRadius": 6,
                                "pointHoverRadius": 8,
                                "pointBackgroundColor": "white",
                                "pointBorderWidth": 2
                            }
                            chart_data["datasets"].append(dataset)
                        
                        dataset["data"].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Add current odds
    if event.bookmakers:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        chart_data["labels"].append(current_time)
        
        for bookmaker in event.bookmakers:
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                    
                for outcome in market["outcomes"]:
                    try:
                        price = float(outcome["price"])
                        # Add to appropriate dataset
                        dataset_name = f"{bookmaker['key']} - {outcome['name']}"
                        dataset = next((d for d in chart_data["datasets"] if d["label"] == dataset_name), None)
                        
                        if not dataset:
                            dataset = {
                                "label": dataset_name,
                                "data": [],
                                "borderColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "backgroundColor": f"hsl({len(chart_data['datasets']) * 30}, 70%, 50%)",
                                "fill": False,
                                "tension": 0.1,
                                "pointRadius": 6,
                                "pointHoverRadius": 8,
                                "pointBackgroundColor": "white",
                                "pointBorderWidth": 2
                            }
                            chart_data["datasets"].append(dataset)
                        
                        dataset["data"].append(price)
                    except (ValueError, KeyError) as e:
                        print(f"[WARNING] Invalid price value for {bookmaker['key']}: {e}")

    # Ensure all datasets have the same length
    max_length = len(chart_data["labels"])
    for dataset in chart_data["datasets"]:
        while len(dataset["data"]) < max_length:
            dataset["data"].append(None)

    print(f"[DEBUG] Generated chart data:")
    print(f"- Timestamps: {len(chart_data['labels'])}")
    print(f"- Datasets: {len(chart_data['datasets'])}")
    for dataset in chart_data["datasets"]:
        print(f"- {dataset['label']}: {len(dataset['data'])} points")

    return jsonify(chart_data)
