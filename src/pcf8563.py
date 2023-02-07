"""src/pcf8563.py.

MicroPython library for NXP PCF8563 Real-time clock/calendar.

Created by Lewis He
[Github: lewisxhe/PCF8563_PythonLibrary](https://github.com/lewisxhe/PCF8563_PythonLibrary)

See LICENSE.
"""

import utime
from machine import I2C
from src.constants import (
    PCF8563_SLAVE_ADDRESS,
    PCF8563_STAT2_REG,
    PCF8563_SEC_REG,
    PCF8563_MIN_REG,
    PCF8563_HR_REG,
    PCF8563_DAY_REG,
    PCF8563_WEEKDAY_REG,
    PCF8563_MONTH_REG,
    PCF8563_YEAR_REG,
    PCF8563_SQW_REG,
    PCF8563_ALARM_AF,
    PCF8563_TIMER_TF,
    PCF8563_ALARM_AIE,
    PCF8563_ALARM_ENABLE,
    PCF8563_ALARM_MINUTES,
    PCF8563_ALARM_HOURS,
    PCF8563_ALARM_DAY,
    PCF8563_ALARM_WEEKDAY,
    CLOCK_CLK_OUT_FREQ_1_HZ
)


class PCF8563:
    """MicroPython driver for the NXP PCF8563 Real-time clock/calendar."""

    def __init__(self, i2c, address=None):
        """Initialize needs to be given an initialized I2C port."""
        self.i2c = i2c
        self.address = address if address else PCF8563_SLAVE_ADDRESS
        self.buffer = bytearray(16)
        self.bytebuf = memoryview(self.buffer[0:1])

    def __write_byte(self, reg, val):
        self.bytebuf[0] = val
        self.i2c.writeto_mem(self.address, reg, self.bytebuf)

    def __read_byte(self, reg):
        self.i2c.readfrom_mem_into(self.address, reg, self.bytebuf)
        return self.bytebuf[0]

    def __bcd2dec(self, bcd):
        return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

    def __dec2bcd(self, dec):
        tens, units = divmod(dec, 10)
        return (tens << 4) + units

    def seconds(self):
        """Get the current allowed seconds of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_SEC_REG) & 0x7F)

    def minutes(self):
        """Get the current allowed minutes of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_MIN_REG) & 0x7F)

    def hours(self):
        """Get the current allowed hours of PCF8563."""
        d = self.__read_byte(PCF8563_HR_REG) & 0x3F
        return self.__bcd2dec(d & 0x3F)

    def day(self):
        """Get the current allowed day of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_WEEKDAY_REG) & 0x07)

    def date(self):
        """Get the current allowed date of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_DAY_REG) & 0x3F)

    def month(self):
        """Get the current allowed month of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_MONTH_REG) & 0x1F)

    def year(self):
        """Get the current allowed year of PCF8563."""
        return self.__bcd2dec(self.__read_byte(PCF8563_YEAR_REG))

    def datetime(self):
        """Return the current datetime in tuple format.

        Tuple format: (year, month, date, hours, minutes, seconds, day)
        """
        return (self.year(), self.month(), self.date(),
                self.hours(), self.minutes(), self.seconds(),
                self.day())

    def write_all(self,
                  year=None,
                  month=None,
                  date=None,
                  hours=None,
                  minutes=None,
                  seconds=None,
                  day=None):
        """Write non-None values to byte registers.

        Range: seconds [0,59], minutes [0,59], hours [0,23],
               day [0,6], date [1-31], month [1-12], year [0-99].
        """
        if seconds is not None:
            if seconds < 0 or seconds > 59:
                raise ValueError('Seconds is out of range [0,59].')
            seconds_reg = self.__dec2bcd(seconds)
            self.__write_byte(PCF8563_SEC_REG, seconds_reg)

        if minutes is not None:
            if minutes < 0 or minutes > 59:
                raise ValueError('Minutes is out of range [0,59].')
            self.__write_byte(PCF8563_MIN_REG, self.__dec2bcd(minutes))

        if hours is not None:
            if hours < 0 or hours > 23:
                raise ValueError('Hours is out of range [0,23].')
            # no 12 hour mode
            self.__write_byte(PCF8563_HR_REG, self.__dec2bcd(hours))

        if year is not None:
            if year < 0 or year > 99:
                raise ValueError('Years is out of range [0,99].')
            self.__write_byte(PCF8563_YEAR_REG, self.__dec2bcd(year))

        if month is not None:
            if month < 1 or month > 12:
                raise ValueError('Month is out of range [1,12].')
            self.__write_byte(PCF8563_MONTH_REG, self.__dec2bcd(month))

        if date is not None:
            if date < 1 or date > 31:
                raise ValueError('Date is out of range [1,31].')
            self.__write_byte(PCF8563_DAY_REG, self.__dec2bcd(date))

        if day is not None:
            if day < 0 or day > 6:
                raise ValueError('Day is out of range [1,7].')
            self.__write_byte(PCF8563_WEEKDAY_REG, self.__dec2bcd(day))

    def set_datetime(self, dt):
        """Input tuple to rtc.

        Tuple format: (year, month, date, hours, minutes, seconds, day)
        """
        self.write_all(year=dt[0] % 100,
                       month=dt[1],
                       date=dt[2],
                       hours=dt[3],
                       minutes=dt[4],
                       seconds=dt[5],
                       day=dt[6])

    def write_now(self):
        """Write the current system time to PCF8563."""
        self.set_datetime(utime.localtime())

    def set_clk_out_frequency(self, frequency=CLOCK_CLK_OUT_FREQ_1_HZ):
        """Set the clock output pin frequency."""
        self.__write_byte(PCF8563_SQW_REG, frequency)

    def check_if_alarm_on(self):
        """Read the register to get the alarm enabled."""
        return bool(self.__read_byte(PCF8563_STAT2_REG) & PCF8563_ALARM_AF)

    def turn_alarm_off(self):
        """Write the register to disable the alarm.

        Should not affect the alarm interrupt state.
        """
        alarm_state = self.__read_byte(PCF8563_STAT2_REG)
        self.__write_byte(PCF8563_STAT2_REG, alarm_state & 0xf7)

    def clear_alarm(self):
        """Clear status register."""
        alarm_state = self.__read_byte(PCF8563_STAT2_REG)
        alarm_state &= ~(PCF8563_ALARM_AF)
        alarm_state |= PCF8563_TIMER_TF
        self.__write_byte(PCF8563_STAT2_REG, alarm_state)

        self.__write_byte(PCF8563_ALARM_MINUTES, 0x80)
        self.__write_byte(PCF8563_ALARM_HOURS, 0x80)
        self.__write_byte(PCF8563_ALARM_DAY, 0x80)
        self.__write_byte(PCF8563_ALARM_WEEKDAY, 0x80)

    def check_for_alarm_interrupt(self):
        """Check for alarm interrupt,is alram int return True."""
        return bool(self.__read_byte(PCF8563_STAT2_REG) & 0x02)

    def enable_alarm_interrupt(self):
        """Turn on the alarm interrupt output to the interrupt pin."""
        alarm_state = self.__read_byte(PCF8563_STAT2_REG)
        alarm_state &= ~PCF8563_ALARM_AF
        alarm_state |= (PCF8563_TIMER_TF | PCF8563_ALARM_AIE)
        self.__write_byte(PCF8563_STAT2_REG, alarm_state)

    def disable_alarm_interrupt(self):
        """Turn off the alarm interrupt output to the interrupt pin."""
        alarm_state = self.__read_byte(PCF8563_STAT2_REG)
        alarm_state &= ~(PCF8563_ALARM_AF | PCF8563_ALARM_AIE)
        alarm_state |= PCF8563_TIMER_TF
        self.__write_byte(PCF8563_STAT2_REG, alarm_state)

    def set_daily_alarm(self,
                        hours=None,
                        minutes=None,
                        date=None,
                        weekday=None):
        """Set alarm match, allow sometimes, minute, day, week."""
        if minutes is None:
            minutes = PCF8563_ALARM_ENABLE
            self.__write_byte(PCF8563_ALARM_MINUTES, minutes)
        else:
            if minutes < 0 or minutes > 59:
                raise ValueError('Minutes is out of range [0,59].')
            self.__write_byte(PCF8563_ALARM_MINUTES,
                              self.__dec2bcd(minutes) & 0x7f)

        if hours is None:
            hours = PCF8563_ALARM_ENABLE
            self.__write_byte(PCF8563_ALARM_HOURS, hours)
        else:
            if hours < 0 or hours > 23:
                raise ValueError('Hours is out of range [0,23].')
            self.__write_byte(PCF8563_ALARM_HOURS, self.__dec2bcd(
                hours) & 0x7f)

        if date is None:
            date = PCF8563_ALARM_ENABLE
            self.__write_byte(PCF8563_ALARM_DAY, date)
        else:
            if date < 1 or date > 31:
                raise ValueError('date is out of range [1,31].')
            self.__write_byte(PCF8563_ALARM_DAY, self.__dec2bcd(
                date) & 0x7f)

        if weekday is None:
            weekday = PCF8563_ALARM_ENABLE
            self.__write_byte(PCF8563_ALARM_WEEKDAY, weekday)
        else:
            if weekday < 0 or weekday > 6:
                raise ValueError('weekday is out of range [0,6].')
            self.__write_byte(PCF8563_ALARM_WEEKDAY, self.__dec2bcd(
                weekday) & 0x7f)
