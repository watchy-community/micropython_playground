"""src/constants.py.

Used to declare that the expression is a constant,
so that the compiler can optimise it.
"""

from micropython import const

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

# Vibrate Motor
VIBRATE_MOTOR = const(13)

# ePaper Display
WHITE = const(1)
BLACK = const(0)
EPD_WIDTH = const(200)
EPD_HEIGHT = const(200)
DISPLAY_CS = const(5)
DISPLAY_DC = const(10)
DISPLAY_RST = const(9)
DISPLAY_BSY = const(19)
DISPLAY_SCK = const(18)
DISPLAY_MOSI = const(23)
DRIVER_OUTPUT_CONTROL = const(0x01)
BOOSTER_SOFT_START_CONTROL = const(0x0C)
GATE_SCAN_START_POSITION = const(0x0F)
DEEP_SLEEP_MODE = const(0x10)
DATA_ENTRY_MODE_SETTING = const(0x11)
SW_RESET = const(0x12)
TEMPERATURE_SENSOR_CONTROL = const(0x1A)
MASTER_ACTIVATION = const(0x20)
DISPLAY_UPDATE_CONTROL_1 = const(0x21)
DISPLAY_UPDATE_CONTROL_2 = const(0x22)
WRITE_RAM = const(0x24)
WRITE_RAM_RED = const(0x26)
WRITE_VCOM_REGISTER = const(0x2C)
WRITE_LUT_REGISTER = const(0x32)
SET_DUMMY_LINE_PERIOD = const(0x3A)
SET_GATE_TIME = const(0x3B)  # not in datasheet
BORDER_WAVEFORM_CONTROL = const(0x3C)
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER = const(0x4F)
TERMINATE_FRAME_READ_WRITE = const(0xFF)  # aka NOOP
BUSY = const(1)  # 1=busy, 0=idle

# RTC & BMA423
BMA_INT1 = const(14)
BMA_INT2 = const(12)
RTC_SDA = const(21)  # Shared with BMA
RTC_SCL = const(22)  # Shared with BMA
RTC_INT = const(27)
PCF8563_SLAVE_ADDRESS = const(0x51)
PCF8563_STAT1_REG = const(0x00)
PCF8563_STAT2_REG = const(0x01)
PCF8563_SEC_REG = const(0x02)
PCF8563_MIN_REG = const(0x03)
PCF8563_HR_REG = const(0x04)
PCF8563_DAY_REG = const(0x05)
PCF8563_WEEKDAY_REG = const(0x06)
PCF8563_MONTH_REG = const(0x07)
PCF8563_YEAR_REG = const(0x08)
PCF8563_SQW_REG = const(0x0D)
PCF8563_TIMER1_REG = const(0x0E)
PCF8563_TIMER2_REG = const(0x0F)
PCF8563_VOL_LOW_MASK = const(0x80)
PCF8563_minuteS_MASK = const(0x7F)
PCF8563_HOUR_MASK = const(0x3F)
PCF8563_WEEKDAY_MASK = const(0x07)
PCF8563_CENTURY_MASK = const(0x80)
PCF8563_DAY_MASK = const(0x3F)
PCF8563_MONTH_MASK = const(0x1F)
PCF8563_TIMER_CTL_MASK = const(0x03)
PCF8563_ALARM_AF = const(0x08)
PCF8563_TIMER_TF = const(0x04)
PCF8563_ALARM_AIE = const(0x02)
PCF8563_TIMER_TIE = const(0x01)
PCF8563_TIMER_TE = const(0x80)
PCF8563_TIMER_TD10 = const(0x03)
PCF8563_NO_ALARM = const(0xFF)
PCF8563_ALARM_ENABLE = const(0x80)
PCF8563_CLK_ENABLE = const(0x80)
PCF8563_ALARM_MINUTES = const(0x09)
PCF8563_ALARM_HOURS = const(0x0A)
PCF8563_ALARM_DAY = const(0x0B)
PCF8563_ALARM_WEEKDAY = const(0x0C)
CLOCK_CLK_OUT_FREQ_32_DOT_768KHZ = const(0x80)
CLOCK_CLK_OUT_FREQ_1_DOT_024KHZ = const(0x81)
CLOCK_CLK_OUT_FREQ_32_KHZ = const(0x82)
CLOCK_CLK_OUT_FREQ_1_HZ = const(0x83)
CLOCK_CLK_HIGH_IMPEDANCE = const(0x0)
