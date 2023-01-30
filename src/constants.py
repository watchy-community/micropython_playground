"""constants.py.

Used to declare that the expression is a constant
so that the compiler can optimise it.
"""

from micropython import const

# ePaper
WHITE = 1
BLACK = 0

# UART
UART_TX = const(1)
UART_RX = const(3)

# Buttons
BTN_MENU = const(26)
BTN_BACK = const(25)
BTN_UP = const(35)
BTN_DOWN = const(4)

# ADC
BATT_ADC = const(34)

# RTC & BMA423
RTC_SDA = const(21)  # Shared with BMA
RTC_SCL = const(22)  # Shared with BMA
RTC_INT = const(27)
BMA_INT1 = const(14)
BMA_INT2 = const(12)

# Vibrate Motor
VIBRATE_MOTOR = const(13)
