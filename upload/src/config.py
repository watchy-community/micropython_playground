"""config.py.

Various configuration options.
"""
# False allows Deepsleep to run, True prevents Deepsleep
DEBUG = False

# Numerical timezone offset
timeZone = -5

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
