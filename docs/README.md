# Project Docs

## Notes

- Each of the original font files has been trimmed to make the final py files smaller.
- The .sfd files are FontForge project files.
- The .ttf files are the output from the FontForge projects.
- Using font_to_py, we turned the font files into python code.

```bash
# The -c option specifies which characters to export into a python file.
# It has made significant reductions in file size.

python font_to_py.py -x -f Monocraft-no-ligatures.ttf 44 monocraft_44.py -c 0123456789:

python font_to_py.py -x -f Monocraft-no-ligatures.ttf 24 monocraft_24.py -c " 0123456789,ADFJMNOSTWabcdeghilnoprtuvy"

# I had to move a couple icons up from the unicode section for this
python font_to_py.py -x -f weathericons-mod.ttf 36 weather_36.py -c ABDEF/

# A and / are 3 bars, R and . are 2 bars, S and - is 1 bar, T and , is 0 bars
python font_to_py.py -x -f Battery-Icons.ttf 36 battery_36.py -c ARST #/.-,
```

## References

- [Github: IdreesInc/Monocraft](https://github.com/IdreesInc/Monocraft)
- [Github: erikflowers/weather-icons](https://github.com/erikflowers/weather-icons)
- [dafont: battery-icons.font](https://www.dafont.com/battery-icons.font)
