# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Tuple, Optional, Iterable, Union)

from ..types import (ColorName, StyleName)


# code of colors
_COLOR_CODE = {
    "d": "0",  # dark/black
    "r": "1",  # red
    "g": "2",  # green
    "y": "3",  # yellow
    "b": "4",  # blue
    "m": "5",  # magenta
    "c": "6",  # cyan
    "w": "7",  # white
}
# code of styles
_STYLE_CODE = {
    "bold": "1",
    "dim": "2",
    "italic": "3",
    "udl": "4",
    "underline": "4",
    "blink": "5",
    "selected": "7",
    "disappear": "8",
    "del": "9",
    "delete": "9"
}


def get_ansi_code(
    fg: Optional[Union[ColorName, int, Iterable[int]]],
    bg: Optional[Union[ColorName, int, Iterable[int]]],
    styles: Iterable[StyleName]
) -> Tuple[str, str]:
    r"""
    Generate ANSI code for style and color.
    """
    def _parse_color(
        c: Union[ColorName, int, Iterable[int]],
        is_fg: bool
    ) -> str:
        r"""
        Parse the color input into ANSI color code.
        """
        parse = ""
        if isinstance(c, str):
            # Basic 8 color OR Light 8 color
            if c in _COLOR_CODE:
                # Basic 8 color
                parse = ("3" if is_fg else "4") + _COLOR_CODE[c]
            elif c.startswith("l") and len(c) == 2 and c[1] in _COLOR_CODE:
                # Light 8 color
                parse = ("9" if is_fg else "10") + _COLOR_CODE[c[1]]
        elif isinstance(c, int) and 0 <= c <= 255:
            # 256 color
            parse = ("38" if is_fg else "48") + f";5;{c}"
        elif isinstance(c, Iterable) and all(isinstance(val, int) and 0 <= val <= 255 for val in c):
            # True color
            rgb = (list(c) + [0, 0, 0])[:3]
            parse = ("38" if is_fg else "48") + f";2;{rgb[0]};{rgb[1]};{rgb[2]}"

        return parse

    # style_code
    if isinstance(styles, Iterable):
        style_code = ";".join(_STYLE_CODE[s] for s in styles if s in _STYLE_CODE)
    else:
        style_code = ""
    # color_code
    foreground = "" if fg is None else _parse_color(fg, is_fg=True)
    background = "" if bg is None else _parse_color(bg, is_fg=False)
    color_code = ";".join((foreground, background)).strip(";")

    return style_code, color_code


def assemble_segments(
    segments: Iterable[Tuple[str, str, str]],
    use_color: bool = True,
    use_style: bool = True
) -> str:
    r"""
    Assemble segments into a single ANSI formatted string.
    """
    result = ""
    for plain, color_code, style_code in segments:
        if not plain:
            continue

        if use_color and use_style:
            codes = f"{style_code};{color_code}"
        elif use_color or use_style:
            codes = color_code if use_color else style_code
        else:
            codes = ""
        codes = codes.strip(";")
        if codes:
            result += f"\033[{codes}m{plain}\033[0m"
        else:
            result += plain

    return result
