import json
import os

from flask import Flask, render_template

from helper import get_stop_locations, get_route_data

app = Flask(__name__)
app.config.from_object(__name__)

MAPBOX_ACCESS_KEY = os.environ.get('MAPBOX_ACCESS_KEY')
DEBUG = os.environ.get('DEBUG')

ROUTE = [{'lat': 51.87622233333333, 'long': 5.7971985,'name': '{Skatokairos olakala}', 'is_stop_location': True},
 {'lat': 51.8982955, 'long': 5.646801166666666,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.90278333333333, 'long': 5.542553,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.90100066666667, 'long': 5.541878333333333,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.8544775, 'long': 5.416200666666667,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.816728166666664, 'long': 5.175681833333333,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.824829, 'long': 4.969789166666667,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.797950166666666, 'long': 4.827218,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.695032499999996, 'long': 4.5069165,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.69839916666667, 'long': 4.424386166666666,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.68235283333333, 'long': 4.395956666666667,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.6836035, 'long': 4.393018666666666,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.683595333333336, 'long': 4.39302,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.683601833333334, 'long': 4.393012,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.683608166666666, 'long': 4.393020833333333,'name': 'Skatokairos', 'is_stop_location': True},
 {'lat': 51.683597, 'long': 4.393012833333334,'name': 'Skatokairos', 'is_stop_location': True}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/route')
def route():
    if not MAPBOX_ACCESS_KEY:
        return 'No Access Key found for Mapbox'

    route_data = get_route_data(MAPBOX_ACCESS_KEY, ROUTE)
    stop_locations = get_stop_locations(ROUTE)
    return render_template(
        'route.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        route_data=route_data,
        stop_locations = stop_locations
    )

if __name__ == '__main__':
    DEBUG = int(os.environ.get('DEBUG', 0)) == 1
    app.run(debug=DEBUG)
