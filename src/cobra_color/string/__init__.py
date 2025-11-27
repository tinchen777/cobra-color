# src/cobra_color/string/__init__.py
"""
String utilities for cobra-color.

Functions
---------
- :func:`ctext()`： Generate a easy-to-use `rich str` instance with perfect support for :class:`str`.
- :func:`compile_template()`： Create a template for generating :class:`ColorStr` instances with preset styles.

Classes
-------
- :class:`ColorStr`： An easy-to-use `rich str` class with perfect support for :class:`str`.
- :class:`ColorTemplate`： A template class for generating :class:`ColorStr` instances with preset styles.
"""

from ._color import (ctext, ColorStr)
from ._template import (compile_template, ColorTemplate)

__all__ = [
    "ctext",
    "ColorStr",
    "compile_template",
    "ColorTemplate"
]
