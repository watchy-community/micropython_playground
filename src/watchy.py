"""watchy.py.

The class for the Watchy hardware.

Based on code from https://github.com/hueyy/watchy_py.
"""

import esp32
import micropython
from time import sleep_ms
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
from src.display import Display
from src.pcf8563 import PCF8563
from src.constants import (
    BTN_MENU,
    BTN_BACK,
    BTN_UP,
    BTN_DOWN,
    RTC_SDA,
    RTC_SCL,
    RTC_INT,
    BATT_ADC,
    WHITE,
    BLACK,
    VIBRATE_MOTOR
)

DEBUG = True


class Watchy:
    """Class for Watchy system."""

    def __init__(self):
        """Class Initializer."""
        # define pins
        self.pin_rtcint = Pin(RTC_INT, Pin.IN)
        self.pin_rtcsda = Pin(RTC_SDA)
        self.pin_rtcscl = Pin(RTC_SCL)
        self.pin_motor = Pin(VIBRATE_MOTOR, Pin.OUT)
        self.pin_battery = Pin(BATT_ADC, Pin.IN)
        self.pin_btnMenu = Pin(BTN_MENU, Pin.IN)
        self.pin_btnBack = Pin(BTN_BACK, Pin.IN)
        self.pin_btnDown = Pin(BTN_DOWN, Pin.IN)
        self.pin_btnUp = Pin(BTN_UP, Pin.IN)

        # watch dog timer, not fed for 30 seconds, causes reboot
        self.wdt = WDT(timeout=30000)
        # timer attempts to feed wdt every 10 seconds
        self.wdt_timer = Timer(0)
        self.wdt_timer.init(
            mode=Timer.PERIODIC,
            period=10000,
            callback=self.feed_wdt
        )

        # MAX 4 TIMERS
        # TODO: create network timer
        # check if connected every 60s or 5 minutes?
        # if connected, pass
        # if not connected, attempt connection to known networks

        # TODO: NTP sync timer?
        # check if network connected every hour
        # if connected, sync rtc to ntp

        # ePaper display init
        self.display = Display()

        # i2c init, rtc init
        i2c = SoftI2C(sda=self.pin_rtcsda, scl=self.pin_rtcscl)
        self.rtc = PCF8563(i2c)

        # analog-to-digital, used for battery
        self.adc = ADC(self.pin_battery)

        # code to be looped by async call
        self.init_interrupts()
        self.handle_wakeup()

        # If debug is False, sleep
        if not DEBUG:
            deepsleep()

    def feed_wdt(self, timer):
        """Prevent the ESP32 from resetting."""
        self.wdt.feed()

    def get_battery_voltage(self) -> float:
        """Use ADC interface to read voltage level."""
        return self.adc.read_uv() / 1000 * 2

    def vibrate_motor(self, intervals_ms):
        """Vibrate the 1020 motor."""
        vibe_on: bool = False
        for i in intervals_ms:
            vibe_on = not vibe_on
            self.pin_motor.value(vibe_on)
            sleep_ms(i)
        self.pin_motor.off()

    def init_interrupts(self):
        """Map the interrupts to inputs."""
        # EXT0 is mapped to RTC INT pin.
        esp32.wake_on_ext0(self.pin_rtcint, esp32.WAKEUP_ALL_LOW)

        buttons = (
            self.pin_btnBack,
            self.pin_btnMenu,
            self.pin_btnDown,
            self.pin_btnUp
        )
        # EXT1 is mapped to all 4 button pins.
        esp32.wake_on_ext1(buttons, esp32.WAKEUP_ANY_HIGH)

    def handle_wakeup(self):
        """Do something with the wakeup call."""
        reason = wake_reason()
        print(reason)  # testing
        if reason is EXT0_WAKE or reason == 0:
            # TODO: Need to get RTC_INT to trigger
            print("RTC wake")
            self.display_watchface()
        elif reason is EXT1_WAKE:
            print("PIN wake")
            # the 2 lines below are for testing until rtc_int is working
            print(self.get_battery_voltage())
            self.display_watchface()  # force display update
        else:
            print("Wake for other reason")
            print(reason)

    def display_watchface(self):
        """Write information out to the ePaper."""
        # TODO: create better display output, new font
        self.display.framebuf.fill(WHITE)
        datetime = self.rtc.datetime()
        (year, month, day, week_day, hours, minutes, _) = datetime
        self.display.display_text(f'{hours}', 10, 15, fira_sans_bold_58, WHITE, BLACK)
        self.display.display_text(f'{minutes}', 10, 80, fira_sans_regular_38, WHITE, BLACK)
        self.display.display_text(f'{week_day}, {day} {month}', 10, 160, fira_sans_regular_28, WHITE, BLACK)
        self.display.update()
