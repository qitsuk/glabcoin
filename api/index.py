# from flask import Flask, render_template
# import random

# app = Flask(__name__, template_folder="../templates", static_folder="../static")

# @app.template_filter()
# def comma_format(value):
#     return f"{value:,}"

# @app.route('/')
# def home():
#     fake_price = round(random.uniform(0.01, 0.1), 4)
#     fake_market_cap = random.randint(1000000, 10000000)
#     fake_supply = random.randint(10000000, 500000000)
#     return render_template('index.html', 
#                            price=fake_price, 
#                            market_cap=fake_market_cap, 
#                            supply=fake_supply)

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, jsonify
import random, json, os
from datetime import datetime
from threading import Thread
import time

# Setup Flask app
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Comma formatting filter
@app.template_filter()
def comma_format(value):
    try:
        return f"{value:,}"
    except (TypeError, ValueError):
        return value

# Path to data file
DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/values.json')

# Background thread to update data
def update_data_periodically():
    while True:
        time.sleep(10)  # Update every 10 seconds
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        if data:
            last_price = data[-1]['price']
            last_supply = data[-1]['supply']
        else:
            last_price = 0.05  # ⬅️ Start value for GlabCoin
            last_supply = 10_000_000

        # Simulate realistic price fluctuation (±2%)
        change_pct = random.uniform(-0.02, 0.02)
        new_price = round(last_price * (1 + change_pct), 4)

        # Cap price to stay above 0.01
        new_price = max(new_price, 0.01)

        # Gradually increase supply
        new_supply = last_supply + random.randint(1000, 5000)

        data.append({
            "timestamp": datetime.utcnow().isoformat(),
            "price": new_price,
            "supply": new_supply
        })

        with open(DATA_FILE, 'w') as f:
            json.dump(data[-100:], f, indent=2)  # Keep last 100 entries

# Homepage
@app.route('/', endpoint='home')
def home():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            latest = data[-1] if data else {"price": 0.0, "supply": 0}
    except (FileNotFoundError, IndexError, json.JSONDecodeError):
        latest = {"price": 0.0, "supply": 0}

    price = latest["price"]
    supply = latest["supply"]
    market_cap = round(price * supply)

    return render_template('index.html',
                           price=price,
                           supply=supply,
                           market_cap=market_cap)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/buy')
def buy():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            latest = data[-1] if data else {"price": 0.05}
    except Exception:
        latest = {"price": 0.05}

    price = latest["price"]
    return render_template('buy.html', price_per_coin=price)

# API endpoint
@app.route('/data')
def data():
    try:
        with open(DATA_FILE, 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify([])

# Start updater in background
Thread(target=update_data_periodically, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
