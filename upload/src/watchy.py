"""src/watchy.py.

The class for the Watchy hardware.

Based on code from https://github.com/hueyy/watchy_py.
"""

from esp32 import wake_on_ext0, wake_on_ext1, WAKEUP_ALL_LOW, WAKEUP_ANY_HIGH
from utime import gmtime, sleep_ms
from ntptime import time as ntptime
from network import WLAN, STA_IF
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
import errno
import json
import assets.fonts.monocraft_48 as monocraft_48
import assets.fonts.monocraft_24 as monocraft_24
import assets.fonts.symbols_36 as symbols_36
from lib.display import Display
from lib.pcf8563 import PCF8563
from src.config import trustedWiFi, timeZone, DEBUG
from src.utils import monthNames, weekDays, check_weather, weatherCondition
from src.constants import (
    BTN_MENU,
    BTN_BACK,
    BTN_UP,
    BTN_DOWN,
    RTC_SDA,
    RTC_SCL,
    RTC_INT,
    WHITE,
    BLACK
)


class Watchy:
    """Class for Watchy system."""

    def __init__(self):
        """Class Initializer."""
        # define pins
        self.pin_rtcint = Pin(RTC_INT, mode=Pin.IN)
        self.pin_rtcsda = Pin(RTC_SDA)
        self.pin_rtcscl = Pin(RTC_SCL)
        self.pin_btnMenu = Pin(BTN_MENU, Pin.IN)
        self.pin_btnBack = Pin(BTN_BACK, Pin.IN)
        self.pin_btnDown = Pin(BTN_DOWN, Pin.IN)
        self.pin_btnUp = Pin(BTN_UP, Pin.IN)

        # define timers - max 4
        # watch dog timer, not fed for 30 seconds, causes reboot
        self.wdt = WDT(timeout=30000)
        # timer attempts to feed wdt every 10 seconds
        self.wdt_timer = Timer(0)
        self.wdt_timer.init(
            mode=Timer.PERIODIC,
            period=10000,
            callback=self.feed_wdt
        )

        # WLAN init
        self.station = WLAN(STA_IF)
        self.station.active(True)

        # ePaper display init
        self.display = Display()

        # i2c init, rtc init
        i2c = SoftI2C(sda=self.pin_rtcsda, scl=self.pin_rtcscl)
        self.rtc = PCF8563(i2c)

        self.init_interrupts()
        self.handle_wakeup()

        # If debug is False, sleep
        if not DEBUG:
            deepsleep()

    def feed_wdt(self, timer):
        """Prevent the ESP32 from resetting."""
        self.wdt.feed()

    def init_interrupts(self):
        """Map the interrupts to inputs."""
        buttons = (
            self.pin_btnBack,
            self.pin_btnMenu,
            self.pin_btnDown,
            self.pin_btnUp
        )
        wake_on_ext0(self.pin_rtcint, WAKEUP_ALL_LOW)
        wake_on_ext1(buttons, WAKEUP_ANY_HIGH)

    def handle_wakeup(self):
        """Do something with the wakeup call."""
        reason = wake_reason()
        datetime = self.rtc.datetime()
        # (year, month, date, hours, minutes, seconds, weekday)
        (_, _, _, hours, minutes, _, day) = datetime
        if reason is EXT0_WAKE or reason == 0:
            print('RTC wake')
            # connect to wifi, update ntp every 4 hours
            if (hours % 4 == 0) and minutes == 0:
                print('4th hour update')
                self.check_network()
                self.check_ntptime()
                check_weather()
            # run every minute
            self.display_watchface()
            self.set_rtc_interrupt(minutes + 1)

        elif reason is EXT1_WAKE:
            print('PIN wake')
            # the lines below are testing until rtc_int/timers are fixed
            self.check_network()
            self.check_ntptime()
            check_weather()
            self.display_watchface()
            self.set_rtc_interrupt(minutes + 1)
        else:
            print('Wake for other reason')
            print(reason)

    def display_watchface(self):
        """Write information out to the ePaper."""
        self.display.framebuf.fill(WHITE)
        datetime = self.rtc.datetime()
        # (year, month, date, hours, minutes, seconds, weekday)
        (_, month, date, hours, minutes, _, day) = datetime

        if month == 0:
            month = 1  # fix boot as month 0

        if len(str(hours)) == 1:
            hours = f'0{hours}'

        if len(str(minutes)) == 1:
            minutes = f'0{minutes}'

        with open('weather.json', 'r') as file:
            weather = json.load(file)

        temp = str(round(weather['current_weather']['temperature']))
        weathercode = weather['current_weather']['weathercode']

        vbat = self.get_battery_voltage()
        print(f'Battery Level: {vbat}')
        if vbat > 4.1:
            batteryLevel = 'a'
        elif vbat > 3.95 and vbat <= 4.1:
            batteryLevel = 'b'
        elif vbat > 3.80 and vbat <= 3.95:
            batteryLevel = 'c'
        else:
            batteryLevel = 'd'

        # Top Row
        self.display.display_text(
            f'{hours}:{minutes}',
            10, 15, monocraft_48, WHITE, BLACK
        )
        # Second Row
#        self.display.display_text(
#            '0123456789',
#            10, 74, monocraft_24, WHITE, BLACK
#        )
        # Third Row
        self.display.display_text(
            batteryLevel,
            10, 106, symbols_36, WHITE, BLACK
        )
        # Fourth Row / Weather
        self.display.display_text(
            '/',
            10, 138, symbols_36, WHITE, BLACK
        )
        self.display.display_text(
            temp,
            25, 138, monocraft_24, WHITE, BLACK
        )
        self.display.display_text(
            f'{weatherCondition[weathercode]}',
            70, 138, symbols_36, WHITE, BLACK
        )
        # Bottom Row
        self.display.display_text(
            f'{weekDays[day]},{monthNames[month - 1]} {date}',
            10, 170, monocraft_24, WHITE, BLACK
        )
        self.display.update()

    def set_rtc_interrupt(self, rtc_minutes):
        """Change the RTC Interrupt alarm."""
        if rtc_minutes == 60:
            rtc_minutes = 00
        print(f'Updating RTC alarm: {rtc_minutes}')
        self.rtc.clear_alarm()
        self.rtc.set_daily_alarm(minutes=rtc_minutes)
        self.rtc.enable_alarm_interrupt()

    def check_network(self):
        """Check the wireless network connection."""
        print('Checking network connection')
        if self.station.isconnected():
            print('Network is already online')
            return
        else:
            print('Scanning for local networks')
            wifiResults = self.station.scan()
            for knownNet in trustedWiFi:
                for scanNet in wifiResults:
                    if scanNet[0].decode() == knownNet[0]:
                        print(f'Connecting to {knownNet[0]}')
                        self.station.connect(knownNet[0], knownNet[1])
                        while not self.station.isconnected():
                            print('Waiting on connection...')
                            sleep_ms(1000)
                        print('Network connection successful')
                        print(self.station.ifconfig())
                        return
            print('Network not connected')

    def check_ntptime(self):
        """Check NTP Server for time, if online."""
        print('Checking online time server')
        if self.station.isconnected():
            print('Network connected, getting ntp update')
            try:
                wantime = ntptime() + (timeZone * 60 * 60)
                localtime = gmtime(wantime)
                self.rtc.set_datetime(localtime)
            except OSError as exc:
                if exc.errno == errno.ETIMEDOUT:
                    print('Connection to NTP timed out')
                else:
                    print('Unknown NTP error')
            print('RTC sync\'d to NTP')
        else:
            print('Not online, ntp unreachable')

    def get_battery_voltage(self):
        """Check the battery voltage level."""
        return self.adc.read_uv() / 1000 * 2
