# src/term-tz/__init__.py
"""
term-tz
-------

A lightweight Python package for terminal display enhancements.

_Example:_
>>> from term_tz import color_str
"""
from .color import ctext
from .format import dict_print, list_print
from .draw import (color_font, printable_image, BinaryImage, render_image)

__author__ = "Zhen Tian"
__version__ = "0.1.0"

__all__ = [
    "ctext",
    "color_font",
    "printable_image",
    "BinaryImage",
    "render_image",
    "dict_print",
    "list_print"
]
