"""utils.py.

These are various utility functions.
"""

import time
from machine import Pin
from constants import VIBRATE_MOTOR


def vibrate_motor(intervals_ms):
    """
    Vibrates for the specified intervals (to be provided in milliseconds)
    :param intervals_ms: intervals should be provided in the following format: [VIBRATE, DELAY, VIBRATE, etc.]
    """
    vibrate_pin = Pin(VIBRATE_MOTOR, Pin.OUT)
    vibrate_on: bool = False
    for i in intervals_ms:
        vibrate_on = not vibrate_on
        vibrate_pin.value(vibrate_on)
        time.sleep_ms(i)
    vibrate_pin.off()