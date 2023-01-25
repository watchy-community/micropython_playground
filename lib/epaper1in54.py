"""
Adapted from MicroPython Waveshare 1.54" Black/White GDEH0154D27 e-paper display driver
https://github.com/mcauser/micropython-waveshare-epaper

MIT License
Copyright (c) 2017 Waveshare
Copyright (c) 2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from time import sleep_ms  # type: ignore

import ustruct
from micropython import const

# Display resolution
EPD_WIDTH = const(200)
EPD_HEIGHT = const(200)

# Display commands
DRIVER_OUTPUT_CONTROL = const(0x01)
BOOSTER_SOFT_START_CONTROL = const(0x0C)
# GATE_SCAN_START_POSITION             = const(0x0F)
DEEP_SLEEP_MODE = const(0x10)
DATA_ENTRY_MODE_SETTING = const(0x11)
SW_RESET = const(0x12)
# TEMPERATURE_SENSOR_CONTROL           = const(0x1A)
MASTER_ACTIVATION = const(0x20)
# DISPLAY_UPDATE_CONTROL_1             = const(0x21)
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


class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    LUT_FULL_UPDATE = bytearray(
        b"\x02\x02\x01\x11\x12\x12\x22\x22\x66\x69\x69\x59\x58\x99\x99\x88\x00\x00\x00\x00\xF8\xB4\x13\x51\x35\x51\x51\x19\x01\x00"
    )
    LUT_PARTIAL_UPDATE = bytearray(
        b"\x10\x18\x18\x08\x18\x18\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x14\x44\x12\x00\x00\x00\x00\x00\x00"
    )

    def send_command(self, command: int, data: bytearray = None):
        self.dc.off()
        self.cs.off()
        self.spi.write(bytearray([command]))
        self.cs.on()
        if data is not None:
            self.send_data(data)

    def send_data(self, data: bytearray):
        self.dc.on()
        self.cs.off()
        self.spi.write(data)
        self.cs.on()

    def init(self):
        self.reset()
        self.send_command(DRIVER_OUTPUT_CONTROL)
        self.send_data(bytearray([((EPD_HEIGHT - 1) >> 8) & 0xFF]))
        self.send_data(bytearray([((EPD_HEIGHT - 1)) & 0xFF]))
        self.send_data(bytearray([0x00]))  # GD = 0 SM = 0 TB = 0
        self.send_command(BOOSTER_SOFT_START_CONTROL, b"\xD7\xD6\x9D")
        self.send_command(WRITE_VCOM_REGISTER, b"\xA8")  # VCOM 7C
        self.send_command(SET_DUMMY_LINE_PERIOD, b"\x1A")  # 4 dummy lines per gate
        self.send_command(SET_GATE_TIME, b"\x08")  # 2us per line
        self.send_command(DATA_ENTRY_MODE_SETTING, b"\x03")  # X increment Y increment
        self.set_lut(self.LUT_FULL_UPDATE)

    def wait_until_idle(self):
        while self.busy.value() == BUSY:
            sleep_ms(100)

    def reset(self):
        self.rst.off()
        sleep_ms(200)
        self.rst.on()
        sleep_ms(200)

    def set_lut(self, lut):
        self.send_command(WRITE_LUT_REGISTER, lut)

    # to wake call reset() or init()
    def sleep(self):
        self.send_command(
            DEEP_SLEEP_MODE
        )  # enter deep sleep , b"\x01" A0=1, A0=0 power on
        self.wait_until_idle()

    def hw_init(self):
        self.wait_until_idle()
        self.send_command(SW_RESET)
        self.wait_until_idle()

        # init code
        self.send_command(DRIVER_OUTPUT_CONTROL)
        self.send_command(0xC7)
        self.send_command(0x00)
        self.send_command(0x00)

        self.send_command(DATA_ENTRY_MODE_SETTING)
        self.send_command(DRIVER_OUTPUT_CONTROL)

        self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self.send_command(0x00)
        self.send_command(0x18)

        self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self.send_command(0xC7)
        self.send_command(0x00)
        self.send_command(0x00)
        self.send_command(0x00)

        self.send_command(BORDER_WAVEFORM_CONTROL)
        self.send_command(0x05)

        self.send_command(0x18)
        self.send_command(0x80)

        self.send_command(SET_RAM_X_ADDRESS_COUNTER)
        self.send_command(0x00)
        self.send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self.send_command(0x00)
        self.wait_until_idle()

    def update(self, partial=False):
        data = bytearray([0xFF if partial else 0xF7])
        self.send_command(DISPLAY_UPDATE_CONTROL_2, data)
        self.send_command(MASTER_ACTIVATION)
        self.wait_until_idle()

    def write_buffer_to_ram(
        self,
        buffer: bytearray,
        x: int = 0,
        y: int = 0,
        w: int = EPD_WIDTH,
        h: int = EPD_HEIGHT,
        invert=False,
        mirror_y=False,
    ):
        """
        Adapted from https://github.com/ZinggJM/GxEPD2
        """
        width_bytes: int = (w + 7) // 8  # width bytes, bitmaps are padded
        x -= x % 8  # byte boundary
        w = width_bytes * 8  # byte boundary
        x1 = 0 if x < 0 else x  # limit
        y1 = 0 if y < 0 else y  # limit
        w1: int = w if x + w < EPD_WIDTH else EPD_WIDTH - x  # limit
        h1: int = h if y + h < EPD_HEIGHT else EPD_HEIGHT - y  # limit
        dx: int = x1 - x
        dy: int = y1 - y
        w1 -= dx
        h1 -= dy
        for i in range(h1):
            for j in range(w1 // 8):
                idx: int = (
                    j + dx // 8 + ((h - 1 - (i + dy))) * width_bytes
                    if mirror_y
                    else j + dx // 8 + (i + dy) * width_bytes
                )
                self.send_data(bytearray([~buffer[idx] if invert else buffer[idx]]))

    def display_buffer(self, buffer: bytearray, mirror_y=True, partial=False):
        self.send_command(WRITE_RAM)
        self.write_buffer_to_ram(buffer, mirror_y=True)
        self.update(partial)
