import os

from flask import Flask, render_template, jsonify

from helper import get_route_data, get_stop_locations
from process import (avg_speed_by_hour, max_wind_speed_by_hour,
                     min_wind_speed_by_hour, num_ships, route_weather_data)

app = Flask(__name__)
app.config.from_object(__name__)

MAPBOX_ACCESS_KEY = os.environ.get('MAPBOX_ACCESS_KEY')
DEBUG = os.environ.get('DEBUG')

ROUTE = [
    {
        'lat': d['lat_msg'],
        'long': d['lon_msg'],
        'is_stop_location': True,
        'title':  ','.join([
            """Station: {0},
               Date: {1},
               Time: {2},
               Weather: {3},
               Temperature: {4} \u00b0C,
               Wind: {5:.2f} km/h
            """.format(
                d['city_name'],
                d['date_msg'],
                d['time_msg'],
                d['description'],
                d['temp'],
                d['wind_spd']
            )
        ])
    }
    for d in route_weather_data
]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/metrics')
def metrics():
    return {
        'num_ships': num_ships,
        'avg_speed_by_hour': avg_speed_by_hour,
        'min_wind_speed_by_hour': min_wind_speed_by_hour,
        'max_wind_speed_by_hour': max_wind_speed_by_hour,
    }


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
        stop_locations=stop_locations
    )


if __name__ == '__main__':
    DEBUG = int(os.environ.get('DEBUG', 0)) == 1
    app.run(debug=DEBUG)
