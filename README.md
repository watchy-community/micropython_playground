# Watchy Micropython Playground

Testing MicroPython with Watchy ESP32 hardware.

## ToDo

- [ ] Get RTC INT to work with pcf8563 driver, or find new driver
- [ ] Get wireless connection working on timer
- [ ] Get NTP sync working with RTC
- [ ] Work on new display layout
  - [ ] new font?
- [ ] Move all `const()` to `src/constants.py`

## Issues

It is not possible to get the wakeup bit in MicroPython yet,
see [GH: micropython/issues/6981](https://github.com/micropython/micropython/issues/6981)