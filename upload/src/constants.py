"""src/constants.py.

Used to declare that the expression is a constant,
so that the compiler can optimise it.
"""

from micropython import const

# Used in src/watchy.py
## Buttons
BTN_MENU = const(26)
BTN_BACK = const(25)
BTN_UP = const(35)
BTN_DOWN = const(4)
## ePaper Display
WHITE = const(1)
BLACK = const(0)
## RTC
RTC_SDA = const(21)  # Shared with BMA
RTC_SCL = const(22)  # Shared with BMA
RTC_INT = const(27)
## ADC
BATT_ADC = const(34)

# Used in lib/display.py
## ePaper Display
DISPLAY_CS = const(5)
DISPLAY_DC = const(10)
DISPLAY_RST = const(9)
DISPLAY_BSY = const(19)
DISPLAY_SCK = const(18)
DISPLAY_MOSI = const(23)
EPD_WIDTH = const(200)  # also used in lib/epaper1in54.py
EPD_HEIGHT = const(200) # also used in lib/epaper1in54.py

# Used in lib/epaper1in54.py
## ePaper Display
BUSY = const(1)  # 1=busy, 0=idle
SW_RESET = const(0x12)
WRITE_RAM = const(0x24)
SET_GATE_TIME = const(0x3B)
DEEP_SLEEP_MODE = const(0x10)
MASTER_ACTIVATION = const(0x20)
WRITE_LUT_REGISTER = const(0x32)
WRITE_VCOM_REGISTER = const(0x2C)
SET_DUMMY_LINE_PERIOD = const(0x3A)
DRIVER_OUTPUT_CONTROL = const(0x01)
BORDER_WAVEFORM_CONTROL = const(0x3C)
DATA_ENTRY_MODE_SETTING = const(0x11)
DISPLAY_UPDATE_CONTROL_2 = const(0x22)
SET_RAM_X_ADDRESS_COUNTER = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER = const(0x4F)
BOOSTER_SOFT_START_CONTROL = const(0x0C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)

# Used in lib/pcf8563.py
## RTC
PCF8563_SLAVE_ADDRESS = const(0x51)
PCF8563_STAT2_REG = const(0x01)
PCF8563_SEC_REG = const(0x02)
PCF8563_MIN_REG = const(0x03)
PCF8563_HR_REG = const(0x04)
PCF8563_DAY_REG = const(0x05)
PCF8563_WEEKDAY_REG = const(0x06)
PCF8563_MONTH_REG = const(0x07)
PCF8563_YEAR_REG = const(0x08)
PCF8563_SQW_REG = const(0x0D)
PCF8563_ALARM_AF = const(0x08)
PCF8563_TIMER_TF = const(0x04)
PCF8563_ALARM_AIE = const(0x02)
PCF8563_ALARM_ENABLE = const(0x80)
PCF8563_ALARM_MINUTES = const(0x09)
PCF8563_ALARM_HOURS = const(0x0A)
PCF8563_ALARM_DAY = const(0x0B)
PCF8563_ALARM_WEEKDAY = const(0x0C)
CLOCK_CLK_OUT_FREQ_1_HZ = const(0x83)
