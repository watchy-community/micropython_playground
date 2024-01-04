"""src/utils.py.

Reference dictionaries, shared functions, and anything used by but not
necessarily apart of the Watchy class.
"""
from errno import ETIMEDOUT
from json import load
from requests import get
from src.config import (
    LATITUDE,
    LONGITUDE,
    UNIT_TEMP,
    UNIT_RAIN,
    UNIT_WIND,
    TIME_ZONE
)
from src.constants import EPOCH70

week_days = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun'
}

month_names = {
    0: 'Jan',
    1: 'Feb',
    2: 'Mar',
    3: 'Apr',
    4: 'May',
    5: 'Jun',
    6: 'Jul',
    7: 'Aug',
    8: 'Sep',
    9: 'Oct',
    10: 'Nov',
    11: 'Dec'
}

weather_condition = {
    0: 'A',   # Clear Sky
    1: 'A',   # Mainly clear
    2: 'B',   # Partly cloudy
    3: 'B',   # Overcast
    45: 'D',  # Fog
    48: 'D',  # Depositing rime fog
    51: 'E',  # Drizzle light
    53: 'E',  # Drizzle moderate
    55: 'E',  # Drizzle dense
    56: 'E',  # Freezing drizzle light
    57: 'E',  # Freezing drizzle dense
    61: 'E',  # Rain slight
    63: 'E',  # Rain moderate
    65: 'E',  # Rain heavy
    66: 'E',  # Freezing rain light
    67: 'E',  # Freezing rain heavy
    71: 'F',  # Snow fall light
    73: 'F',  # Snow fall moderate
    75: 'F',  # Snow fall heavy
    77: 'F',  # Snow grains
    80: 'E',  # Rain showers light
    81: 'E',  # Rain showers moderate
    82: 'E',  # Rain showers violent
    85: 'F',  # Snow showers slight
    86: 'F',  # Snow showers heavy
    95: 'E',  # Thunderstorms
    96: 'E',  # Thunderstorms with slight hail
    99: 'E'   # Thunderstorms with heavy hail
}


def get_weather():
    """Get weather from Open-Meteo.com."""
    headers = {
        'User-Agent': '(Watchy ESP32, lee.rowland@gmail.com)'
    }
    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}', \
             f'&longitude={LONGITUDE}&daily=weathercode,temperature_2m_max,', \
             'temperature_2m_min,wind_speed_10m_max,wind_direction_10m_dominant', \
             f'&temperature_unit={UNIT_TEMP}&wind_speed_unit={UNIT_WIND}', \
             f'&precipitation_unit={UNIT_RAIN}&timeformat=unixtime&forecast_days=1', \
             f'&timezone={TIME_ZONE}'
    print('Checking weather updates')
    try:
        response = get(api_url, headers=headers)
        with open('weather.json', 'w', encoding='UTF-8') as file:
            file.write(response.content)
    except OSError as exc:
        if exc.errno == ETIMEDOUT:
            print('Connection to weather API timed out')
        else:
            print(exc)


def read_weather():
    """Read weather.json and return values."""
    with open('weather.json', 'r', encoding='UTF-8') as file:
        weather = load(file)
    return {
        'tempmax': str(round(weather['daily']['temperature_2m_max'][0])),
        'tempmin': str(round(weather['daily']['temperature_2m_min'][0])),
        'weathercode': weather['daily']['weathercode'][0],
        'windspeed': weather['daily']['wind_speed_10m_max'][0],
        'winddir': weather['daily']['wind_direction_10m_dominant'][0]
    }


def get_ntptime():
    """Grab NTP time from WorldTimeAPI.

    MicroPython uses the 2000 EPOCH when calculating time, therefore we must
    subtract the seconds since the 1970 EPOCH from the WorldTimeAPI `unixtime`
    to get the 2000 EPOCH. From there we use the first 3 characters of the
    `utc_offset` (ie: -05 at time of writing), multiplied by 3600
    """
    try:
        response = get(f'http://worldtimeapi.org/api/timezone/{TIME_ZONE}')
    except OSError as exc:
        if exc.errno == ETIMEDOUT:
            print('Connection to DST check timed out.')
            return False
        else:
            print('Unknown DST error')
            return False
    return (response.json()['unixtime'] - EPOCH70) + \
           (int(response.json()['utc_offset'][0:3]) * 3600)


def get_vbat_level(vbat):
    """Return the font character for each batter level."""
    # Max 4.2, Min 2.7
    if vbat > 3.825:
        battery_level = 'A'
    elif vbat > 3.45 and vbat <= 3.825:
        battery_level = 'R'
    elif vbat > 3.075 and vbat <= 3.45:
        battery_level = 'S'
    else:
        battery_level = 'T'
    return battery_level
