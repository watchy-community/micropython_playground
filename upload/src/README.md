# SRC DIRECTORY

Consider the `src` directory the heart of the project. The files that live here are used across the project for their various purposes.

- `config.py` : This file is used to set individuals distinct settings, such as wifi ssid and password, timezone, latitude and longitude, etc.
- `constants.py` : This file contains unchanging variables used by the system, such as Pin assignments, Bytecode for displays, etc.
- `utils.py` : These functions are utilitarian, they are not apart of the Watchy class because they are unrelated to how the watch functions.
- `watchy.py` : This is the true heart of the project, the `Watchy` class is defined here, with methods, properties, etc.