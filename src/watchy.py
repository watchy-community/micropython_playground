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
import assets.fonts.monocraft_48 as monocraft_48
import assets.fonts.monocraft_32 as monocraft_32
import assets.fonts.monocraft_24 as monocraft_24
from src.display import Display
from src.pcf8563 import PCF8563
from src.wifi import trustedWiFi
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

DEBUG = False
TIMEOFFSET = -6


class Watchy:
    """Class for Watchy system."""

    def __init__(self):
        """Class Initializer."""
        # define pins
        self.pin_rtcint = Pin(RTC_INT, mode=Pin.IN)
        self.pin_rtcsda = Pin(RTC_SDA)
        self.pin_rtcscl = Pin(RTC_SCL)
        self.pin_motor = Pin(VIBRATE_MOTOR, Pin.OUT)
        self.pin_battery = Pin(BATT_ADC, Pin.IN)
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

        # analog-to-digital, used for battery
        self.adc = ADC(self.pin_battery)

        self.init_interrupts()
        self.handle_wakeup()

        # If debug is False, sleep
        if not DEBUG:
            deepsleep()

    def feed_wdt(self, timer):
        """Prevent the ESP32 from resetting."""
        self.wdt.feed()

    def set_rtc_interrupt(self, rtc_minutes):
        """Change the RTC Interrupt alarm."""
        alarmTime = rtc_minutes
        if alarmTime == 60:
            alarmTime = 00
        self.rtc.clear_alarm()
        print(f'RTC_MINUTES: {alarmTime}')
        self.rtc.set_daily_alarm(minutes=alarmTime)
        self.rtc.enable_alarm_interrupt()

    def check_network(self):
        """Check the wireless network connection."""
        print('Checking network connection...')
        if self.station.isconnected():
            print('Already connected.')
            return
        else:
            wifiResults = self.station.scan()
            for knownNet in trustedWiFi:
                for scanNet in wifiResults:
                    if scanNet[0].decode() == knownNet[0]:
                        self.station.connect(knownNet[0], knownNet[1])
                        while not self.station.isconnected():
                            pass
                        print('Connection successful.')
                        print(self.station.ifconfig())
                        return
            print('Wireless not connected.')
            return

    def check_ntptime(self):
        """Check NTP Server for time, if online."""
        print('Checking online time server...')
        if self.station.isconnected():
            print('Getting ntp update...')
            wantime = ntptime()
            localtime = gmtime(wantime)
            dstHour = localtime[3] + TIMEOFFSET
            newtime = (
                localtime[0],  # year
                localtime[1],  # month
                localtime[2],  # date
                dstHour,       # hours
                localtime[4],  # minutes
                localtime[5],  # seconds
                localtime[6]   # day of the week
            )
            self.rtc.set_datetime(newtime)
        else:
            print('Not online.')

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
            print("RTC wake")
            # connect to wifi, update ntp every 4 hours
            if (hours % 4 == 0) and minutes == 0:
                self.check_network()
                self.check_ntptime()
            # run every minute
            self.display_watchface()
            self.set_rtc_interrupt(minutes + 1)

        elif reason is EXT1_WAKE:
            print("PIN wake")
            # the lines below are testing until rtc_int/timers are fixed
            #print(self.get_battery_voltage())
            self.display_watchface()
            self.set_rtc_interrupt(minutes + 1)
        else:
            print("Wake for other reason")
            print(reason)

    def display_watchface(self):
        """Write information out to the ePaper."""
        weekDays = {
            0: 'Mon',
            1: 'Tue',
            2: 'Wed',
            3: 'Thu',
            4: 'Fri',
            5: 'Sat',
            6: 'Sun'
        }
        monthNames = {
            0: 'Jan',  # boot from dead, month is 0, keyerror
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        }
        self.display.framebuf.fill(WHITE)
        datetime = self.rtc.datetime()
        # (year, month, date, hours, minutes, seconds, weekday)
        (_, month, date, hours, minutes, _, day) = datetime

        if len(str(hours)) == 1:
            hours = f'0{hours}'

        if len(str(minutes)) == 1:
            minutes = f'0{minutes}'

        """
        Watchy screen is 200x200
        at 48px font, it is 5 characters wide
        at 32px font, it is 8 characters wide
        at 24px font, it is 10 characters wide

        There may be a little more room if you start more left than 10px.
        """
        self.display.display_text(f'{hours}:{minutes}', 10, 15, monocraft_48, WHITE, BLACK)
        self.display.display_text(f'01234567', 10, 80, monocraft_32, WHITE, BLACK)
        self.display.display_text(f'0123456789', 10, 125, monocraft_24, WHITE, BLACK)
        self.display.display_text(f'{weekDays[day]}, {monthNames[month]} {date}', 10, 160, monocraft_24, WHITE, BLACK)
        self.display.update()
