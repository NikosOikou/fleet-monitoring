import datetime
import json

import numpy as np
import pandas as pd

PATH_RAW_MESSAGES = './data/raw_messages.csv'
PATH_WEATHER_DATA = './data/weather_data.json'
PATH_RAW_MESSAGES_PROCESSED = './data/raw_messages_processed.csv'


def distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a1 = np.sin(dlat / 2.0) ** 2
    a2 = np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    a = a1 + a2
    return 6367 * 2 * np.arcsin(np.sqrt(a))


def clean_up_raw_messages(input_file, output_file):
    msg = pd.read_csv(input_file)
    temp = msg['raw_message'].str.split(',', expand=True)
    temp.rename(columns={
        0: 'status',
        1: 'lat',
        2: 'lat_dir',
        3: 'lon',
        4: 'lon_dir',
        5: 'speed',
        6: 'track',
        7: 'date',
        8: 'var',
        9: 'var_dir'}, inplace=True)
    cols = [
        'device_id',
        'datetime',
        'address_ip',
        'address_port',
        'original_message_id'
    ]
    msg = pd.concat([msg[cols], temp], axis=1)
    msg['lat'] = msg['lat'].str.replace('[%&@$*]', '').astype(float)
    msg['lon'] = msg['lon'].str.replace('[%&@$*]', '').astype(float)
    msg['track'] = msg['track'].str.replace('[%&@$*]', '').astype(float)
    msg['speed'] = msg['speed'].str.replace('[%&@$*]', '').astype(float)
    msg['unix_datetime'] = msg['datetime']
    msg['datetime'] = pd.to_datetime(msg['datetime'], unit='s')
    msg['date'] = msg['datetime'].dt.date
    msg['time'] = msg['datetime'].dt.time
    msg['year'] = msg['datetime'].dt.year
    msg['month'] = msg['datetime'].dt.month
    msg['hour'] = msg['datetime'].dt.hour
    msg['var'] = msg['var'].astype(float)
    msg['lat_dir'] = msg['lat_dir'].str.replace('[%&@$*]', '')
    msg['lon_dir'] = msg['lon_dir'].str.replace('[%&@$*]', '')

    msg.to_csv(output_file, index=False)

    return msg


msg = clean_up_raw_messages(
    input_file=PATH_RAW_MESSAGES,
    output_file=PATH_RAW_MESSAGES_PROCESSED
)

# Metric 1: For how many ships do we have available data
num_ships = msg['device_id'].nunique()

# Metric 2: Avg speed for all available ships for each hour of
# the date 2019-02-13
filtered = msg[msg['date'] == datetime.date(2019, 2, 13)]
grouped = filtered.groupby('hour')
to_dict = grouped['speed'].mean().round(2).to_dict()
avg_speed_by_hour = {int(k): v for k, v in to_dict.items()}

# Load weather data
with open(PATH_WEATHER_DATA) as data_file:
    weath_json = json.load(data_file)

cols = [
    'timezone',
    'state_code',
    'country_code',
    'lat',
    'lon',
    'city_name',
    'station_id',
    'sources',
    'city_id'
]
weath = pd.io.json.json_normalize(weath_json, 'data', cols)

temp = weath['weather'].dropna().apply(pd.Series)
weath = pd.concat([weath, temp], axis=1)
weath.drop('weather', axis=1, inplace=True)
weath['datetime'] = pd.to_datetime(weath['datetime'], format='%Y-%m-%d:%H')
weath['date'] = weath['datetime'].dt.date
weath['time'] = weath['datetime'].dt.time
weath['year'] = weath['datetime'].dt.year
weath['month'] = weath['datetime'].dt.month
weath['hour'] = weath['datetime'].dt.hour

# Metric 3: Max & min wind speed for every available day
# for ship ”st-1a2090” only
grouped = weath.groupby('hour')['wind_spd']
min_wind_speed_by_hour = grouped.apply(min).to_dict()
max_wind_speed_by_hour = grouped.apply(max).to_dict()

# Metric 4: Visualize full weather conditions (example fields: general
# description, temperature, wind speed) across route of the ship ”st-1a2090”
# for date 2019-02-13.
msg = msg[
    (msg['date'] == datetime.date(2019, 2, 13)) &
    (msg['device_id'] == 'st-1a2090')
]
df = pd.merge(msg, weath, on='hour', suffixes=('_msg', '_weath'))
df['dist'] = distance(
    df['lon_msg'],
    df['lat_msg'],
    df['lon_weath'],
    df['lat_weath']
)

idx = df.groupby('original_message_id')['dist'].transform('min') == df['dist']
df = df[idx]
df = df.groupby('station_id').apply(min).to_dict('records')

route_weather_data = sorted(df, key=lambda i: i['unix_datetime'])
