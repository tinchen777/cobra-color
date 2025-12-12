# src/cobra_color/__init__.py
"""
cobra-color
===========

A lightweight Python package for terminal display enhancements.

Modules
-------
- :mod:`cobra_color.string`: Colored string manipulation and generation.
- :mod:`cobra_color.render`: Rendering utilities for rendering text and images in the terminal.
- :mod:`cobra_color.format`: Formatting utilities for structured data display.
- :mod:`cobra_color.output`: Output utilities for smart printing in the terminal.
Functions
---------
- :func:`ctext()`: Generate a easy-to-use `rich str` instance with perfect support for :class:`str`.
- :func:`to_ansi()`: Convert an object to an ANSI formatted :class:`ExtStr`.
- :func:`smart_print()`: A smart print function that works well with progress bars from `tqdm` and `rich` consoles.
- :func:`set_console_func()`: Set a global console for smart_print function.

Examples
--------

Render a text in the terminal::

    from cobra_color import ctext, smart_print

    c_text_1 = ctext("Hello World!", fg="r", styles=["bold"])
    # Print directly from the terminal
    print(c_text_1)

    c_text_2 = ctext("Hello World!", fg=(255, 255, 255), styles=["udl", "bold"])
    # Alternatively, you can use `smart_print()` to automatically support progress bar modes like tqdm and rich.
    smart_print(c_text_2)

    # Merge `c_text_1` and `c_text_2` while preserving their colors and style formatting.
    c_text_3 = c_text_1 + c_text_2

    # You can continue to use str's proprietary functions and keep the existing colors and styles.
    c_text_1.upper()

Render an image in the terminal:

    from cobra_color.render import imgfile_to_ansi, smart_print

    # ASCII art
    smart_print(imgfile_to_ansi("example.jpg", width=80, mode="ascii"))

    # Half-block color (recommended for truecolor terminals)
    imgfile_to_ansi("example.jpg", width=80, mode="half-color", display=True)

Render some text with fonts in the terminal:

    from cobra_color.draw import fonttext_to_ansi, FontName, smart_print

    # Borderless grayscale font
    smart_print(fonttext_to_ansi(
        "Hello World!",
        font=FontName.LLDISCO,
        mode="half-gray",
        trim_border=True
    ))
"""

from .string import (ctext, to_ansi)
from .output import (smart_print, set_console)


__author__ = "Zhen Tian"
__version__ = "1.0.2"

__all__ = [
    "ctext",
    "to_ansi",
    "smart_print",
    "set_console"
]
