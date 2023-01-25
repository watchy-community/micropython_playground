from constants import BLACK, WHITE
from lib.epaper1in54 import EPD
from lib.writer import Writer
from machine import Pin, SPI
import framebuf

# fonts
import assets.fonts.fira_sans_regular_24 as fira_sans_regular_24


class Display:

    BACKGROUND = 0
    FOREGROUND = 1

    MAX_WIDTH = 200
    MAX_HEIGHT = 200

    def __init__(self):
        cs = Pin(5, Pin.OUT, value=1)
        dc = Pin(10, Pin.OUT, value=0)
        reset = Pin(9, Pin.OUT, value=0)
        busy = Pin(19, Pin.IN)

        sck = Pin(18)
        mosi = Pin(23)
        miso = Pin(19)  # appears not to be used but is mandatory

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
        self.buffer = bytearray(self.MAX_WIDTH * self.MAX_HEIGHT // 8)
        self.framebuf = framebuf.FrameBuffer(
            self.buffer,
            self.MAX_WIDTH,
            self.MAX_HEIGHT,
            framebuf.MONO_HLSB,
        )
        self.epd.init()
        self.epd.hw_init()

    def update(self, buffer: bytearray | None = None, mirror_y=True, partial=False):
        target_buffer = self.buffer if buffer is None else buffer
        self.epd.display_buffer(target_buffer, mirror_y=mirror_y, partial=partial)

    def fill(self, color: int):
        self.framebuf.fill(color)
        self.update()

    def sleep(self):
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
        wri = Writer(
            self.framebuf,
            font,
            self.MAX_WIDTH,
            self.MAX_HEIGHT,
            background_colour,
            text_colour,
        )
        wri.set_textpos(self.framebuf, y, x)
        wri.printstring(text)
