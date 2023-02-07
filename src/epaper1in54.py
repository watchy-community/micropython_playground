"""src/epaper1in54.py.

Adapted from MicroPython Waveshare 1.54" Black/White GDEH0154D27 e-paper
display driver.

Created by Mike Causer
[Github: mcauser/micropython-waveshare-epaper](https://github.com/mcauser/micropython-waveshare-epaper)

See LICENSE.
"""

from time import sleep_ms  # type: ignore
from src.constants import (
    EPD_HEIGHT,
    EPD_WIDTH,
    BUSY,
    SW_RESET,
    WRITE_RAM,
    SET_GATE_TIME,
    DEEP_SLEEP_MODE,
    MASTER_ACTIVATION,
    WRITE_LUT_REGISTER,
    WRITE_VCOM_REGISTER,
    SET_DUMMY_LINE_PERIOD,
    DRIVER_OUTPUT_CONTROL,
    BORDER_WAVEFORM_CONTROL,
    DATA_ENTRY_MODE_SETTING,
    DISPLAY_UPDATE_CONTROL_2,
    SET_RAM_X_ADDRESS_COUNTER,
    SET_RAM_Y_ADDRESS_COUNTER,
    BOOSTER_SOFT_START_CONTROL,
    SET_RAM_X_ADDRESS_START_END_POSITION,
    SET_RAM_Y_ADDRESS_START_END_POSITION,
)


class EPD:
    """MicroPython driver for Waveshare GDEH0154D27 e-paper."""

    def __init__(self, spi, cs, dc, rst, busy):
        """Initialize the class instance."""
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
        """Write command across Serial interface."""
        self.dc.off()
        self.cs.off()
        self.spi.write(bytearray([command]))
        self.cs.on()
        if data is not None:
            self.send_data(data)

    def send_data(self, data: bytearray):
        """Write data across Serial interface."""
        self.dc.on()
        self.cs.off()
        self.spi.write(data)
        self.cs.on()

    def init(self):
        """Initialize the ePaper software."""
        self.reset()
        self.send_command(DRIVER_OUTPUT_CONTROL)
        self.send_data(bytearray([((EPD_HEIGHT - 1) >> 8) & 0xFF]))
        self.send_data(bytearray([((EPD_HEIGHT - 1)) & 0xFF]))
        self.send_data(bytearray([0x00]))  # GD = 0 SM = 0 TB = 0
        self.send_command(BOOSTER_SOFT_START_CONTROL, b"\xD7\xD6\x9D")
        self.send_command(WRITE_VCOM_REGISTER, b"\xA8")  # VCOM 7C
        self.send_command(SET_DUMMY_LINE_PERIOD, b"\x1A")  # 4 lines per gate
        self.send_command(SET_GATE_TIME, b"\x08")  # 2us per line
        self.send_command(DATA_ENTRY_MODE_SETTING, b"\x03")  # X inc Y inc
        self.set_lut(self.LUT_FULL_UPDATE)

    def wait_until_idle(self):
        """Wait for the ePaper to not be busy."""
        while self.busy.value() == BUSY:
            sleep_ms(100)

    def reset(self):
        """Issue RESET command to ePaper hardware."""
        self.rst.off()
        sleep_ms(200)
        self.rst.on()
        sleep_ms(200)

    def set_lut(self, lut):
        """Send waveform to ePaper."""
        self.send_command(WRITE_LUT_REGISTER, lut)

    # to wake call reset() or init()
    def sleep(self):
        """Place ePaper in deep sleep power mode."""
        self.send_command(
            DEEP_SLEEP_MODE
        )  # enter deep sleep , b"\x01" A0=1, A0=0 power on
        self.wait_until_idle()

    def hw_init(self):
        """Initialize the ePaper hardware."""
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
        """Update the display control state."""
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
        """Send buffer data to Serial interface."""
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
                self.send_data(
                    bytearray([~buffer[idx] if invert else buffer[idx]])
                )

    def display_buffer(self, buffer: bytearray, mirror_y=True, partial=False):
        """Send buffer to Serial interface."""
        self.send_command(WRITE_RAM)
        self.write_buffer_to_ram(buffer, mirror_y=True)
        self.update(partial)
