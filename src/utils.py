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


def check_weather():
    """Get weather from Open-Meteo.com."""
    headers = {
        'User-Agent': '(Watchy ESP32, lee.rowland@gmail.com)'
    }
    apiUrl = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&temperature_unit={tempUnit}&windspeed_unit={windUnit}&precipitation_unit={rainUnit}&timezone={weatherTZ}'
    print('Checking weather updates')
    try:
        response = get(apiUrl, headers=headers)
    except OSError as exc:
        if exc.errno == errno.ETIMEDOUT:
            print('Connection to weather API timed out')
        else:
            print('Unknown API error')
        return {}
    return response.json()
