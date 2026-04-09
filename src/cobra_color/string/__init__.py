# src/cobra_color/string/__init__.py
"""
String utilities for :pkg:`cobra_color`.

Functions
---------
- :func:`cstr`: Generate an easy-to-use `rich str` instance with perfect support for :class:`str`.
- :func:`to_ansi`: Convert an object to an ANSI formatted :class:`ExtStr`.
- :func:`to_plain`: Convert an object to a plain :class:`str`.
- :func:`to_cstr`: Convert an object to a :class:`ColorStr`.
- :func:`ansi_to_segments`: Parse an ANSI formatted string into a list of :class:`ColorSeg` segments.
Classes
-------
- :class:`ColorStr`: An easy-to-use `rich str` class with perfect support for :class:`str`.
- :class:`ExtStr`: An `extended str` class that extends the built-in :class:`str` class.
- :class:`ColorSeg`: A segment of color and style information for :class:`ColorStr`.

Examples
--------
- Create a styled :class:`ColorStr` with :func:`cstr`::

    from cobra_color.string import cstr
    cs = cstr("Hello", cstr("World"), fg="r", styles={"bold"}, sep=" ")

- Strip all color information to a plain string with :func:`to_plain`::

    from cobra_color.string import cstr, to_plain
    cs = cstr("Hello World", fg="g")
    to_plain(cs)  # 'Hello World'
    to_plain(42)  # '42'

- Produce an ANSI-formatted string directly with :func:`to_ansi`::

    from cobra_color.string import to_ansi
    s = to_ansi("Hello", fg="r", styles={"bold"})
    s.startswith("\\x1b[") and s.endswith("\\x1b[0m")

- Parse an ANSI string into :class:`ColorSeg` segments with :func:`ansi_to_segments`::

    from cobra_color.string import ansi_to_segments
    segs = ansi_to_segments("\\x1b[31mHello\\x1b[0m World")
    len(segs)  # 2
    segs[0].plain  # 'Hello'

- Rebuild a :class:`ColorStr` parsed from an ANSI string with :func:`to_cstr`::

    from cobra_color.string import to_cstr
    cs = to_cstr("\\x1b[1;32mGreen bold\\x1b[0m")
"""

from ._color import (cstr, to_ansi, to_plain, to_cstr, ColorStr)
from ._extension import ExtStr
from ._segment import (ColorSeg, ansi_to_segments)

__all__ = [
    "cstr",
    "to_ansi",
    "to_plain",
    "to_cstr",
    "ColorStr",
    "ExtStr",
    "ColorSeg",
    "ansi_to_segments"
]
