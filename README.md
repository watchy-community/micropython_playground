# Watchy Micropython Playground

Testing MicroPython with Watchy ESP32 hardware.

## ToDo

- [ ] Get RTC INT to work with pcf8563 driver, or find new driver
- [ ] Get wireless connection working on timer
  - [x] Wireless `check_network` method written
  - [x] Tested method with button interrupt
  - [ ] Not connected out of sleep, is this expected? is it a problem to reconnect each time?
- [ ] Get NTP sync working on timer
  - [x] NTP `check_ntptime` method written
  - [x] Tested method with button interrupt
  - [x] NTP set time on RTC
  - [ ] Add daylight savings check
  - [ ] Add timezone offset
- [ ] Work on new display layout
  - [ ] new font?
- [ ] Move all `const()` to `src/constants.py`
- [ ] Trim libraries to reduce memory usage
  - [ ] pcf8563 has a lot of extra methods we don't use
  - [ ] check display
  - [ ] check epaper1in54
  - [ ] check writer

## Issues

- It is not possible to get the wakeup bit in MicroPython yet, see [GH: micropython/issues/6981](https://github.com/micropython/micropython/issues/6981)
- Second and Third timers don't appear to be running, commented out for now

## Hardware/Datasheets

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