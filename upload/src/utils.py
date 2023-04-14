"""src/utils.py.

Reference dictionaries, shared functions, and anything used by but not
necessarily apart of the Watchy class.
"""
from errno import ETIMEDOUT
from ujson import load
from urequests import get
from src.config import (
    latitude,
    longitude,
    tempUnit,
    windUnit,
    rainUnit,
    weatherTZ
)
from src.constants import EPOCH70

weekDays = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun'
}

monthNames = {
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

weatherCondition = {
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
    86: 'F'   # Snow showers heavy
}


def check_weather():
    """Get weather from Open-Meteo.com."""
    headers = {
        'User-Agent': '(Watchy ESP32, lee.rowland@gmail.com)'
    }
    apiUrl = ''.join((
        f'https://api.open-meteo.com/v1/forecast?latitude={latitude}',
        f'&longitude={longitude}&current_weather=true',
        f'&temperature_unit={tempUnit}&windspeed_unit={windUnit}',
        f'&precipitation_unit={rainUnit}&timezone={weatherTZ}'
    ))
    print('Checking weather updates')
    try:
        response = get(apiUrl, headers=headers)
        with open('weather.json', 'w') as file:
            file.write(response.content)
    except OSError as exc:
        if exc.errno == ETIMEDOUT:
            print('Connection to weather API timed out')
        else:
            print('Unknown API error')


def read_weather():
    """Read weather.json and return values."""
    with open('weather.json', 'r') as file:
        weather = load(file)
    temp = str(round(weather['current_weather']['temperature']))
    weathercode = weather['current_weather']['weathercode']
    return temp, weathercode


def get_ntptime():
    """Grab NTP time from WorldTimeAPI.

    MicroPython uses the 2000 EPOCH when calculating time, therefore we must
    subtract the seconds since the 1970 EPOCH from the WorldTimeAPI `unixtime`
    to get the 2000 EPOCH. From there we use the first 3 characters of the
    `utc_offset` (ie: -05 at time of writing), multiplied by 3600
    """
    try:
        response = get(f'http://worldtimeapi.org/api/timezone/{weatherTZ}')
    except OSError as exc:
        if exc.errno == ETIMEDOUT:
            print('Connection to DST check timed out.')
            return False
        else:
            print('Unknown DST error')
            return False
    return (response.json()['unixtime'] - EPOCH70) + \
           (int(response.json()['utc_offset'][0:3]) * 3600)


def get_vbatLevel(vbat):
    """Return the font character for each batter level."""
    if vbat > 1.91:
        batteryLevel = 'A'
    elif vbat > 1.714 and vbat <= 1.909:
        batteryLevel = 'R'
    elif vbat > 1.519 and vbat <= 1.713:
        batteryLevel = 'S'
    else:
        batteryLevel = 'T'
    return batteryLevel
