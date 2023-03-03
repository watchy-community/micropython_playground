"""src/display.py.

A display driver written for the Watchy ESP32 open-source hardware watch.

Created by Huey Lee
[Github: hueyy/watchy_py](https://github.com/hueyy/watchy_py)

See LICENSE.
"""

import framebuf
from machine import Pin, SPI
from lib.epaper1in54 import EPD
from lib.writer import Writer
from src.constants import (
    DISPLAY_CS,
    DISPLAY_DC,
    DISPLAY_BSY,
    DISPLAY_RST,
    DISPLAY_SCK,
    DISPLAY_MOSI,
    EPD_HEIGHT,
    EPD_WIDTH
)


class Display:
    """MicroPython driver for the Watchy display."""

    BACKGROUND = 0
    FOREGROUND = 1

    def __init__(self):
        """Initialize the class instance."""
        cs = Pin(DISPLAY_CS, Pin.OUT, value=1)
        dc = Pin(DISPLAY_DC, Pin.OUT, value=0)
        reset = Pin(DISPLAY_RST, Pin.OUT, value=0)
        busy = Pin(DISPLAY_BSY, Pin.IN)

        sck = Pin(DISPLAY_SCK)
        mosi = Pin(DISPLAY_MOSI)
        miso = Pin(DISPLAY_BSY)

        spi = SPI(
            1,
            baudrate=20000000,
            polarity=0,
            sck=sck,
            mosi=mosi,
            miso=miso,
        )
        self.epd = EPD(spi=spi, cs=cs, dc=dc, rst=reset, busy=busy)
        self.current_x = 0
        self.current_y = 0
        self.buffer = bytearray(EPD_WIDTH * EPD_HEIGHT // 8)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer,
            EPD_WIDTH,
            EPD_HEIGHT,
            framebuf.MONO_HLSB,
        )
        self.epd.init()
        self.epd.hw_init()

    def update(self,
               buffer: bytearray | None = None,
               mirror_y=True,
               partial=False):
        """Push Framebuffer content to ePaper display."""
        target_buffer = self.buffer if buffer is None else buffer
        self.epd.display_buffer(target_buffer,
                                mirror_y=mirror_y,
                                partial=partial)

    def fill(self, color: int):
        """Fill framebuffer with single color to wipe display."""
        self.framebuf.fill(color)
        self.update()

    def sleep(self):
        """Use ePaper sleep method."""
        self.epd.sleep()

    def display_text(
        self,
        text: str,
        x: int,
        y: int,
        font,
        background_colour: int,
        text_colour: int,
    ):
        """Use Writer object to Framebuffer."""
        wri = Writer(
            self.framebuf,
            font,
            EPD_WIDTH,
            EPD_HEIGHT,
            background_colour,
            text_colour,
            verbose=False
        )
        wri.set_textpos(self.framebuf, y, x)
        wri.printstring(text)
