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
import assets.fonts.fira_sans_bold_58 as fira_bold_58
import assets.fonts.fira_sans_regular_38 as fira_reg_38
import assets.fonts.fira_sans_regular_28 as fira_reg_28
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
        self.pin_rtcint = Pin(RTC_INT, Pin.IN)
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

        # check if connected every 5 minutes
        self.station = WLAN(STA_IF)
        self.station.active(True)
        '''self.sta_timer = Timer(1)
        self.sta_timer.init(
            mode=Timer.ONE_SHOT,
            period=30000,
            callback=self.check_network
        )'''

        # check if network connected every hour
        '''self.ntp_timer = Timer(2)
        self.ntp_timer.init(
            mode=Timer.ONE_SHOT,
            period=60000,
            callback=self.check_ntptime
        )'''

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
                        while self.station.isconnected() == False:
                            pass
            print('Connection successful.')
            print(self.station.ifconfig())

    def check_ntptime(self):
        """Check NTP Server for time, if online."""
        print('Checking online time server...')
        if self.station.isconnected():
            print('Getting ntp update...')
            wantime = ntptime()
            localtime = gmtime(wantime)
            dayOfWeek = localtime[6] + 1  # rtc needs day as 1-7, not 0-6
            dstHour = localtime[3] + TIMEOFFSET
            newtime = (
                localtime[0],  # year
                localtime[1],  # month
                localtime[2],  # date
                dstHour,       # hours
                localtime[4],  # minutes
                localtime[5],  # seconds
                dayOfWeek      # day of the week
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
        # EXT0 is mapped to RTC INT pin.
        wake_on_ext0(self.pin_rtcint, WAKEUP_ALL_LOW)
        # EXT1 is mapped to all 4 button pins.
        wake_on_ext1(buttons, WAKEUP_ANY_HIGH)

    def handle_wakeup(self):
        """Do something with the wakeup call."""
        reason = wake_reason()
        if reason is EXT0_WAKE or reason == 0:
            # TODO: Need to get RTC_INT to trigger
            print("RTC wake")
            self.display_watchface()
        elif reason is EXT1_WAKE:
            print("PIN wake")
            # the 4 lines below are for testing until rtc_int is working
            print(self.get_battery_voltage())
            self.check_network()
            self.check_ntptime()
            self.display_watchface()  # force display update
        else:
            print("Wake for other reason")
            print(reason)

    def display_watchface(self):
        """Write information out to the ePaper."""
        weekDays = {
            0: 'Mon',  # boot from dead, day is 0, keyerror
            1: 'Mon',
            2: 'Tue',
            3: 'Wed',
            4: 'Thu',
            5: 'Fri',
            6: 'Sat',
            7: 'Sun'
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
        # TODO: create better display output, new font
        self.display.framebuf.fill(WHITE)
        datetime = self.rtc.datetime()
        (year, month, date, day, hours, minutes, _) = datetime
        self.display.display_text(f'{hours}:{minutes}', 10, 15, fira_bold_58, WHITE, BLACK)
        self.display.display_text(f'line2', 10, 80, fira_reg_38, WHITE, BLACK)
        self.display.display_text(f'line3', 10, 125, fira_reg_28, WHITE, BLACK)
        self.display.display_text(f'{weekDays[day]}, {monthNames[month]} {date}', 10, 160, fira_reg_28, WHITE, BLACK)
        self.display.update()
