# src/cobra_color/render/__init__.py
"""
Rendering Module for :pkg:`cobra_color` package.

The following dependency libraries are required:
- `Pillow`
- `NumPy`

Functions
---------
- :func:`imgfile_to_ansi`: Convert an image file to a string representation based on the specified mode.
- :func:`fonttext_to_ansi`: Render colored text based on a specified font into a string representation.
- :func:`image_to_ansi`: Render an image (`PIL.Image.Image`) into a string representation based on the specified mode.
- :func:`binarize_image`: Create a binary image from the given source based on the specified threshold and RGB colors.
- :func:`trim_image_border`: Trim the border of the image that matches the specified value.

Classes
-------
- :class:`FontName`: Enum for built-in font names.

Examples
--------
- Render an image file as ASCII art::

    from cobra_color.render import imgfile_to_ansi

    preview = imgfile_to_ansi("example.jpg", mode="ascii", width=40)

- Render font text using a built-in font::

    from cobra_color.render import FontName, fonttext_to_ansi

    preview = fonttext_to_ansi("Hello World!", font=FontName.LLDISCO, mode="half-color")
"""

from .fonts import FontName
try:
    from ._ansi_art import (imgfile_to_ansi, fonttext_to_ansi)
    from ._utils import (image_to_ansi, binarize_image, trim_image_border)
except ImportError:
    from ..exceptions import ModuleUnavailableError
    raise ModuleUnavailableError(
        "`cobra_color.render` module is unavailable, "
        "optional dependency `Pillow`, `NumPy` are required. "
        "Install it via: pip install cobra-color[render]"
    ) from None

__all__ = [
    "imgfile_to_ansi",
    "fonttext_to_ansi",
    "FontName",
    "image_to_ansi",
    "binarize_image",
    "trim_image_border"
]
