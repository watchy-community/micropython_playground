# Watchy Micropython Playground

<img src="face.png" height="50%" width="50%">

Testing MicroPython with Watchy ESP32 hardware.

## ToDo

- [ ] Get NTP sync working ~~on timer~~
  - [x] NTP `check_ntptime` method written
  - [x] Tested method with button interrupt
  - [x] NTP set time on RTC
  - [ ] Add daylight savings check
  - [x] Add timezone offset
- [ ] Work on new display layout
  - [x] new font - changed to monocraft
  - [x] add graphics - used weather icons font
  - [x] adjust screen layout for weather
- [ ] Add weather check code
  - [x] Get weather from Open-Meteo.com
  - [ ] Store weather to file, lost on deepsleep, read from file on display_watchface()
- [ ] Add docstrings to libraries, clean up errors/warnings
  - [x] pcf8563
  - [x] display
  - [x] epaper1in54
  - [ ] writer
- [ ] Reduce memory usage
  - [ ] Change [const() with prefix _](https://docs.micropython.org/en/latest/develop/optimizations.html#variables)
  - [ ] [Cross-compile files as mpy](https://docs.micropython.org/en/latest/develop/optimizations.html#frozen-bytecode)

## Issues

- It is not possible to get the wakeup bit in MicroPython yet, see [GH: micropython/issues/6981](https://github.com/micropython/micropython/issues/6981)
- Adding `ulogging` module from [Github: iabdalkader/micropython-ulogging](https://github.com/iabdalkader/micropython-ulogging) put me over memory allocation limits
  - Reducing memory usage may help make this possible

## References

- [Github: hueyy/watchy_py](https://github.com/hueyy/watchy_py) - this project is largely based on this code
- [Github: mcauser/micropython-waveshare-epaper](https://github.com/mcauser/micropython-waveshare-epaper) - ePaper driver
- [Github: peterhinch/micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py) - Writer interface and font-to-py script
- [Github: lewisxhe/PCF8563_PythonLibrary](https://github.com/lewisxhe/PCF8563_PythonLibrary) - RTC driver for Watchy v2
- [Sync time in MicroPython using NTP](https://bhave.sh/micropython-ntp/) - used section on Timezones
- [MicroPython Documentation](https://docs.micropython.org/en/latest/)

## Hardware/Datasheets

- Microcontroller: [ESP32-PICO-D4](https://www.espressif.com/sites/default/files/documentation/esp32-pico-d4_datasheet_en.pdf)
- USB-Serial: [CP2104](https://www.silabs.com/documents/public/data-sheets/cp2104.pdf)
- E-Paper Display: [GDEH0154D67](https://www.e-paper-display.com/products_detail/productId=455.html)
  - Watchy screen is 200x200
  - at 48px font, it is 5 characters wide
  - at 32px font, it is 8 characters wide
  - at 24px font, it is 10 characters wide
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
