"""src/utils.py.

Reference dictionaries, shared functions, and anything used by but not
necessarily apart of the Watchy class.
"""
import errno
from urequests import get
from src.config import (
    latitude,
    longitude,
    tempUnit,
    windUnit,
    rainUnit,
    weatherTZ
)

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
    45: 'F',  # Fog
    48: 'F',  # Depositing rime fog
    51: 'J',  # Drizzle light
    53: 'J',  # Drizzle moderate
    55: 'J',  # Drizzle dense
    56: 'S',  # Freezing drizzle light
    57: 'S',  # Freezing drizzle dense
    61: 'T',  # Rain slight
    63: 'T',  # Rain moderate
    65: 'T',  # Rain heavy
    66: 'S',  # Freezing rain light
    67: 'S',  # Freezing rain heavy
    71: 'S',  # Snow fall light
    73: 'S',  # Snow fall moderate
    75: 'S',  # Snow fall heavy
    77: 'S',  # Snow grains
    80: 'T',  # Rain showers light
    81: 'T',  # Rain showers moderate
    82: 'T',  # Rain showers violent
    85: 'S',  # Snow showers slight
    86: 'S'   # Snow showers heavy
}


def check_weather():
    """Get weather from Open-Meteo.com."""
    headers = {
        'User-Agent': '(Watchy ESP32, lee.rowland@gmail.com)'
    }
    apiUrl = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&temperature_unit={tempUnit}&windspeed_unit={windUnit}&precipitation_unit={rainUnit}&timezone={weatherTZ}'
    print('Checking weather updates')
    try:
        response = get(apiUrl, headers=headers)
        with open('weather.json', 'w') as file:
            file.write(response.content)
    except OSError as exc:
        if exc.errno == errno.ETIMEDOUT:
            print('Connection to weather API timed out')
        else:
            print('Unknown API error')
