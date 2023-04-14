"""config.py.

Various configuration options.
"""
# Watchy Version
WATCHY_VERSION = 2.0

# False allows Deepsleep to run, True prevents Deepsleep
DEBUG = False

# A list of tuples
# tuple should be SSID then PSK as strings
trustedWiFi = [
    # ('ssid', 'psk')
]

# Weather API for Open-Meteo.com
latitude = '38.95'
longitude = '-92.33'
tempUnit = 'fahrenheit'
windUnit = 'mph'
rainUnit = 'inch'
weatherTZ = 'America%2FChicago'
