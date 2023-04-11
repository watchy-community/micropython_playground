"""src/watchy.py.

The class for the Watchy hardware.

Based on code from https://github.com/hueyy/watchy_py.
"""

from esp32 import wake_on_ext0, wake_on_ext1, WAKEUP_ALL_LOW, WAKEUP_ANY_HIGH
from utime import gmtime, sleep_ms
from ntptime import time as ntptime
from network import WLAN, STA_IF
from errno import ETIMEDOUT
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
import assets.fonts.monocraft_44 as monocraft_44
import assets.fonts.monocraft_24 as monocraft_24
import assets.fonts.battery_36 as battery_36
import assets.fonts.weather_36 as weather_36
from lib.display import Display
from lib.pcf8563 import PCF8563
from src.config import trustedWiFi, timeZone, DEBUG
from src.utils import (
    monthNames,
    weekDays,
    weatherCondition,
    check_weather,
    read_weather
)
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
    BLACK
)


class Watchy:
    """Class for Watchy system."""

    def __init__(self):
        """Class Initializer."""
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
        i2c = SoftI2C(sda=Pin(RTC_SDA), scl=Pin(RTC_SCL))
        self.rtc = PCF8563(i2c)

        # Battery
        self.adc = ADC(Pin(BATT_ADC, Pin.IN))
        self.adc.atten(ADC.ATTN_11DB)
        # self.adc.width(ADC.WIDTH_12BIT)

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
            Pin(BTN_BACK, Pin.IN),
            Pin(BTN_MENU, Pin.IN),
            Pin(BTN_DOWN, Pin.IN),
            Pin(BTN_UP, Pin.IN)
        )
        wake_on_ext0(Pin(RTC_INT, mode=Pin.IN), WAKEUP_ALL_LOW)
        wake_on_ext1(buttons, WAKEUP_ANY_HIGH)

    def handle_wakeup(self):
        """Do something with the wakeup call."""
        reason = wake_reason()
        # (year, month, date, hours, minutes, seconds, weekday)
        (_, month, date, hours, minutes, _, day) = self.rtc.datetime()
        if reason is EXT0_WAKE or reason == 0:
            print('RTC wake')
            # connect to wifi, update ntp at 03:00am
            if hours == 3 and minutes == 0:
                print('3am ntp update')
                self.check_network()
                self.check_ntptime()
                check_weather()
            # run every minute during waking hours
            if hours >= 6 and hours <= 23:
                self.display_watchface(month, date, hours, minutes, day)
                self.set_rtc_interrupt(minutes + 1)
            else:
                self.set_rtc_interrupt(minutes + 1)

        elif reason is EXT1_WAKE:
            print('PIN wake')
            # the lines below are testing until rtc_int/timers are fixed
            self.check_network()
            self.check_ntptime()
            check_weather()
            self.display_watchface(month, date, hours, minutes, day)
            self.set_rtc_interrupt(minutes + 1)
        else:
            print('Wake for other reason')
            print(reason)

    def display_watchface(self, month, date, hours, minutes, day):
        """Write information out to the ePaper."""
        self.display.framebuf.fill(WHITE)

        if month == 0:
            month = 1  # fix boot as month 0

        if len(str(hours)) == 1:
            hours = f'0{hours}'

        if len(str(minutes)) == 1:
            minutes = f'0{minutes}'

        weather = read_weather()
        vbat = self.get_battery_voltage()
        batteryLevel = self.check_battery_level()

        # Top Row
        self.display.display_text(
            f'{hours}:{minutes}',
            10, 15, monocraft_44, WHITE, BLACK
        )
        # Second Row / Testing
        self.display.display_text(
            str(vbat),
            10, 70, monocraft_24, WHITE, BLACK
        )
        # Fourth Row / Weather
        self.display.display_text(
            '/',
            10, 133, weather_36, WHITE, BLACK
        )
        self.display.display_text(
            weather[0],
            28, 138, monocraft_24, WHITE, BLACK
        )
        self.display.display_text(
            f'{weatherCondition[weather[1]]}',
            86, 133, weather_36, WHITE, BLACK
        )
        self.display.display_text(
            batteryLevel,
            160, 123, battery_36, WHITE, BLACK
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
                self.rtc.set_datetime(
                    gmtime(
                        ntptime() + (timeZone * 60 * 60)
                    )
                )
            except OSError as exc:
                if exc.errno == ETIMEDOUT:
                    print('Connection to NTP timed out')
                else:
                    print('Unknown NTP error')
            print('RTC sync\'d to NTP')
        else:
            print('Not online, ntp unreachable')

    def get_battery_voltage(self):
        """Check the battery voltage level.

        The `read_uv` is in microVolts. `read_uv` / 1000 is milliVolts, which
        is the unit Arduino uses. milliVolts / 1000 is Volts.
        1000 * 1000 = 1,000,000 or 1e6.
        According to Arduino code, there is a voltage divider on the board so
        the voltage is divided by 2.0 to compensate.
        """
        return (self.adc.read_uv() / 1e6) / 2.0

    def check_battery_level(self):
        """Check the battery voltage and return battery level code."""
        vbat = self.get_battery_voltage()
        if vbat > 1.91:
            batteryLevel = 'A'
        elif vbat > 1.714 and vbat <= 1.909:
            batteryLevel = 'R'
        elif vbat > 1.519 and vbat <= 1.713:
            batteryLevel = 'S'
        else:
            batteryLevel = 'T'
        return batteryLevel
