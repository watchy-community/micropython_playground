# Removed Constants

The following variable definitions were removed from `src/constants.py` to
trim down the file and free up memory. I've placed them here in case they
are needed for future work.

```python
"""src/constants.py"""
# UART
UART_TX = const(1)
UART_RX = const(3)
# Vibrate Motor
VIBRATE_MOTOR = const(13)
# ePaper Display
GATE_SCAN_START_POSITION = const(0x0F)
TEMPERATURE_SENSOR_CONTROL = const(0x1A)
DISPLAY_UPDATE_CONTROL_1 = const(0x21)
WRITE_RAM_RED = const(0x26)
TERMINATE_FRAME_READ_WRITE = const(0xFF)  # aka NOOP
# RTC & BMA423
BMA_INT1 = const(14)
BMA_INT2 = const(12)
PCF8563_STAT1_REG = const(0x00)
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
PCF8563_TIMER_TIE = const(0x01)
PCF8563_TIMER_TE = const(0x80)
PCF8563_TIMER_TD10 = const(0x03)
PCF8563_NO_ALARM = const(0xFF)
PCF8563_CLK_ENABLE = const(0x80)
CLOCK_CLK_OUT_FREQ_32_DOT_768KHZ = const(0x80)
CLOCK_CLK_OUT_FREQ_1_DOT_024KHZ = const(0x81)
CLOCK_CLK_OUT_FREQ_32_KHZ = const(0x82)
CLOCK_CLK_HIGH_IMPEDANCE = const(0x0)
```
