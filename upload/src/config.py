"""config.py.

Various configuration options.
"""
# False allows Deepsleep to run, True prevents Deepsleep
DEBUG = False

# A list of tuples
# tuple should be SSID then PSK as strings
trustedWiFi = [
    # ('ssid', 'psk')
]

# Weather API for Open-Meteo.com
LATITUDE = '38.95'
LONGITUDE = '-92.33'
UNIT_TEMP = 'fahrenheit'
UNIT_WIND = 'mph'
UNIT_RAIN = 'inch'
TIME_ZONE = 'America%2FChicago'
