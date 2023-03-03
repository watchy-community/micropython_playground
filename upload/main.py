"""main.py.

Documenting and testing Watchy ESP32 v2 hardware.
"""

import uasyncio as asyncio
from src.watchy import Watchy


async def main():
    """Initialize the Watchy class object."""
    w = Watchy()


asyncio.run(main())
