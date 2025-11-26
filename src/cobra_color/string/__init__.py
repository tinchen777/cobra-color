# src/cobra_color/string/__init__.py
"""
String utilities for cobra-color.

Functions
---------
- :func:`ctext()`： Generate a colored string for terminal output.
- :func:`compile_template()`： Create a template for generating colored strings with preset styles.

Classes
-------
- :class:`ColorStr`： A string class that supports ANSI color and style formatting while preserving plain text.
- :class:`ColorTemplate`： A template class for generating colored strings with preset styles.
"""

from ._color import (ctext, ColorStr)
from ._template import (compile_template, ColorTemplate)

__all__ = [
    "ctext",
    "ColorStr",
    "compile_template",
    "ColorTemplate"
]
