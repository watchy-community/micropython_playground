"""watchy.py.

The class for the Watchy hardware.

Based on code from https://github.com/hueyy/watchy_py.
"""

import time
import esp32
import micropython
from lib.display import Display
from lib.pcf8563 import PCF8563
from machine import (
    EXT0_WAKE,
    EXT1_WAKE,
    Pin,
    SoftI2C,
    ADC,
    WDT,
    Timer,
    wake_reason,
    deepsleep
)
import assets.fonts.fira_sans_bold_58 as fira_sans_bold_58
import assets.fonts.fira_sans_regular_38 as fira_sans_regular_38
import assets.fonts.fira_sans_regular_28 as fira_sans_regular_28
from constants import (
    BTN_MENU,
    BTN_BACK,
    BTN_UP,
    BTN_DOWN,
    RTC_SDA,
    RTC_SCL,
    RTC_INT,
    BATT_ADC,
    WHITE,
    BLACK
)

DEBUG = False

class Watchy:
    def __init__(self):
        self.wdt = WDT(timeout=30000)
        self.wdt_timer = Timer(0)
        self.wdt_timer.init(mode=Timer.PERIODIC, period=10000, callback=self.feed_wdt)
        
        self.display = Display()
        i2c = SoftI2C(sda=Pin(RTC_SDA), scl=Pin(RTC_SCL))
        self.rtc = PCF8563(i2c)
        # set rtc alarm interrupt
        self.adc = ADC(Pin(BATT_ADC, Pin.IN))
        
        self.init_interrupts()
        self.handle_wakeup()
        if not DEBUG:
            deepsleep()


    def feed_wdt(self, timer):
        self.wdt.feed()


    def get_battery_voltage(self) -> float:
        return self.adc.read_uv() / 1000 * 2


    def init_interrupts(self):
        esp32.wake_on_ext0(Pin(RTC_INT, Pin.IN), esp32.WAKEUP_ALL_LOW)
        
        buttons = (
            Pin(BTN_MENU, Pin.IN),
            Pin(BTN_BACK, Pin.IN),
            Pin(BTN_DOWN, Pin.IN),
            Pin(BTN_UP, Pin.IN)
        )
        esp32.wake_on_ext1(buttons, esp32.WAKEUP_ANY_HIGH)
        # NOTE: it is not possible to get the wakeup bit in MicroPython yet
        # see https://github.com/micropython/micropython/issues/6981


    def handle_wakeup(self):
        reason = wake_reason()
        if reason is EXT0_WAKE or reason == 0:
            print("RTC wake")
            self.display_watchface()
        elif reason is EXT1_WAKE:
            print("PIN wake")
            p = Pin(BTN_MENU, Pin.IN)
            print(p.value())
            # force display update
            self.display_watchface()
        else:
            print("Wake for other reason")
            print(reason)


    def display_watchface(self):
        self.display.framebuf.fill(WHITE)
        datetime = self.rtc.datetime()
        (year, month, day, week_day, hours, minutes, _) = datetime
        self.display.display_text(f'{hours}', 10, 15, fira_sans_bold_58, WHITE, BLACK)
        self.display.display_text(f'{minutes}', 10, 80, fira_sans_regular_38, WHITE, BLACK)
        self.display.display_text(f'{week_day}, {day} {month}', 10, 160, fira_sans_regular_28, WHITE, BLACK)
        self.display.update()