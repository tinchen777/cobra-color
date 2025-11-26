# src/cobra_color/draw/__init__.py
"""
Drawing utilities for cobra-color.

Functions
---------
- :func:`fmt_font()`: Render colored text based on a specified font into a string representation.
- :func:`fmt_image()`: Convert an image file to a string representation based on the specified mode.
- :func:`render_image()`: Render an image (`PIL.Image.Image`) into a string representation based on the specified mode.
- :func:`to_bin_image()`: Create a binary image from the given source based on the specified threshold and RGB colors.
- :func:`trim_image_border()`: Trim the border of the image that matches the specified value.

Classes
-------
- :class:`FontName`: Enum for built-in font names.
"""

from ._font import fmt_font
from ._image import fmt_image
from .fonts import FontName
from ._utils import (render_image, to_bin_image, trim_image_border)


__all__ = [
    "fmt_font",
    "fmt_image",
    "FontName",
    "render_image",
    "to_bin_image",
    "trim_image_border"
]
