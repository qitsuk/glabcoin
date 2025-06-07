from flask import Flask, render_template
import random

app = Flask(__name__, template_folder="../templates", static_folder="../static")

@app.template_filter()
def comma_format(value):
    return f"{value:,}"

@app.route('/')
def home():
    fake_price = round(random.uniform(0.01, 0.1), 4)
    fake_market_cap = random.randint(1000000, 10000000)
    fake_supply = random.randint(10000000, 500000000)
    return render_template('index.html', 
                           price=fake_price, 
                           market_cap=fake_market_cap, 
                           supply=fake_supply)



# if __name__ == '__main__':
#     app.run(debug=True)

def handler(environ, start_response):
    from werkzeug.wsgi import DispatcherMiddleware
    from werkzeug.serving import run_simple

    return app(environ, start_response)
