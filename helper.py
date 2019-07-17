import requests
from geojson import Feature, Point

# Mapbox driving direction API call
ROUTE_URL = 'https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson'


def get_stop_locations(route):
    stop_locations = []
    for route_index, location in enumerate(route):
        point = Point([location['long'], location['lat']])
        properties = {
            'title': location['title'],
            'icon': 'campsite',
            'marker-color': '#3bb2d0',
            'marker-symbol': route_index + 1,
            'route_index': route_index
        }
        stop_location = Feature(geometry=point, properties=properties)
        stop_locations.append(stop_location)
    return stop_locations


def get_route_data(mapbox_access_key, route):
    lat_longs = ';'.join([
        '{0},{1}'.format(point['long'], point['lat'])
        for point in route])
    route_url = ROUTE_URL.format(lat_longs, mapbox_access_key)
    result = requests.get(route_url)
    data = result.json()
    geometry = data['routes'][0]['geometry']
    return Feature(geometry=geometry, properties={})
