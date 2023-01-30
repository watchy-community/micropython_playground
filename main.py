"""main.py.

Documenting and testing Watchy ESP32 v2 hardware.

Hardware/Datasheets:

- Microcontroller: [ESP32-PICO-D4](https://www.espressif.com/sites/default/files/documentation/esp32-pico-d4_datasheet_en.pdf)
- USB-Serial: [CP2104](https://www.silabs.com/documents/public/data-sheets/cp2104.pdf)
- E-Paper Display: [GDEH0154D67](https://www.e-paper-display.com/products_detail/productId=455.html)
- Display Connector: [AFC07-S24ECC-00](https://datasheet.lcsc.com/szlcsc/1811021340_JUSHUO-AFC07-S24ECC-00_C11092.pdf)
- 3-Axis Accelerometer: [BMA423](https://watchy.sqfmi.com/assets/files/BST-BMA423-DS000-1509600-950150f51058597a6234dd3eaafbb1f0.pdf)
- Real Time Clock v1.5/2.0: [PCF8563](https://www.mouser.com/datasheet/2/302/PCF8563-1127619.pdf)
- Battery: [LiPo 3.7V 200mAH](https://www.powerstream.com/lip/GMB042030.pdf)
- LDO Voltage Regulator: [ME6211C33M5G-N](https://datasheet.lcsc.com/szlcsc/Nanjing-Micro-One-Elec-ME6211C33M5G-N_C82942.pdf)
- Battery Connector: [BOOMELE 1.25T-2PWT](https://datasheet.lcsc.com/szlcsc/1811092210_BOOMELE-Boom-Precision-Elec-1-25T-2PWT_C22074.pdf)
- Micro-USB Connector: [U-F-M5DD-Y-L](https://datasheet.lcsc.com/szlcsc/1811131825_Korean-Hroparts-Elec-U-F-M5DD-Y-L_C91146.pdf)
- Tactile Buttons: [K2-1114SA-A4SW-06](https://datasheet.lcsc.com/szlcsc/1810061013_Korean-Hroparts-Elec-K2-1114SA-A4SW-06_C136662.pdf)
- Vibration Motor: [1020](https://github.com/SeeedDocument/Bazaar_doc/raw/master/316040001/1020_datasheet.doc)
- PCB Antenna: [SWRA117D](https://www.ti.com/lit/an/swra117d/swra117d.pdf)
"""

import uasyncio as asyncio
from src.watchy import Watchy


async def main():
    w = Watchy()


asyncio.run(main())
