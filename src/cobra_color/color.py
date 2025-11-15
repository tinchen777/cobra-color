# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from functools import cached_property
from typing import (Any, List, Tuple, Optional, Iterable, Union)

from .types import (ColorName, StyleName)


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


def ctext(
    text: Any,
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
) -> ColorStr:
    r"""
    Generate a colored string for terminal output.

    Parameters
    ----------
        text : Any
            The text content to be colored.

        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            - _ColorName_: `Basic 8 color` OR `Light 8 color`, compatible with older terminals;

            NOTE: _ColorName_: `d`(black); `r`(red); `g`(green); `y`(yellow); `b`(blue); `m`(magenta); `c`(cyan); `w`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable[int]_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

            - `None`: No color applied.

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as `fg`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.

            NOTE: _StyleName_: `bold`, `dim`, `italic`, `udl`, `underline`, `blink`, `selected`, `disappear`, `del`, `delete`.

    Returns
    -------
        ColorStr
            The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties. You can combine multiple colored strings using `+` operator or `+=` operator.
    """
    return ColorStr.from_str(text, fg=fg, bg=bg, styles=styles)


class ColorStr(str):
    r"""
    A string class that supports ANSI color and style formatting while preserving plain text.

    NOTE 1: Usage same as `str`, with `plain`, `color_only`, `style_only` properties.

    NOTE 2: The `str` output functions from str class (like `upper()`, `lower()`, etc.) are overridden to preserve color and style formatting for non-combined ColorStr.
    """
    _SEGMENTS: List[Tuple[str, str, str]]  # list of (plain, color_codes, style_codes)
    _is_colored: bool

    @classmethod
    def from_str(
        cls,
        _str: Any,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        r"""
        Create a ColorStr from a regular string with specified color and style.
        """
        plain = str(_str)
        obj = super().__new__(cls, plain)
        # segments
        if plain and (fg is not None or bg is not None or styles is not None):
            style_code, color_code = _get_ansi_code(
                fg=fg,
                bg=bg,
                styles=styles if styles is not None else []
            )
        else:
            style_code = ""
            color_code = ""
        obj._SEGMENTS = [(plain, color_code, style_code)]
        obj._is_colored = bool(color_code or style_code)

        return obj

    def __new__(
        cls,
        *segments: Tuple[str, str, str]
    ):
        # check segments
        is_colored = False
        for seg in segments:
            try:
                if seg[1] != "" or seg[2] != "":
                    is_colored = True
            except Exception:
                raise ValueError("Each Segment Must Be A Tuple Of (plain, color_code, style_code).")

        obj = super().__new__(cls, _assemble_segments(
            segments,
            use_color=False,
            use_style=False
        ))
        obj._SEGMENTS = list(segments)
        obj._is_colored = is_colored

        return obj

    def iscombined(self) -> bool:
        r"""
        Check if the ColorStr is combined from multiple segments.
        """
        return len(self._SEGMENTS) > 1

    def iscolored(self) -> bool:
        r"""
        Check if the ColorStr has any color or style applied.
        """
        return self._is_colored

    def apply_to(
        self,
        text: Any,
        use_color: bool = True,
        use_style: bool = True,
        segment_idx: int = 0
    ) -> ColorStr:
        r"""
        Apply the color and style of a specific segment to a new text.

        Parameters
        ----------
            text : Any
                The text content to be colored.

            use_color : bool, default to `True`
                Whether to apply color codes.

            use_style : bool, default to `True`
                Whether to apply style codes.

            segment_idx : int, default to `0`
                The index of the segment to use for color and style.

        Returns
        -------
            ColorStr
                The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties.

        Raises
        ------
            IndexError
                If the segment index is out of range.
        """
        try:
            _, color_code, style_code = self._SEGMENTS[segment_idx]
        except IndexError:
            raise IndexError(f"Segment Index {segment_idx} Out Of Range, Must Be 0 <= index < {len(self._SEGMENTS)}.")

        return ColorStr((
            text.plain if isinstance(text, ColorStr) else str(text),
            color_code if use_color else "",
            style_code if use_style else ""
        ))

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        if callable(attr):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if isinstance(result, str) and not isinstance(result, ColorStr) and not self.iscombined():
                    return self.apply_to(result)
                return result
            return wrapper
        return attr

    def __add__(self, other_str: str):
        if isinstance(other_str, ColorStr):
            other_segments = other_str._SEGMENTS
        else:
            other_segments = [(str(other_str), "", "")]
        return ColorStr(*(self._SEGMENTS + other_segments))

    def __mul__(self, n: Any):
        assert isinstance(n, int), "Can Only Multiply ColorStr By An Integer."
        if n <= 0:
            return ColorStr()
        return ColorStr(*self._SEGMENTS * n)

    def __str__(self):
        return self.rich

    def __repr__(self):
        return repr(self.rich)

    @cached_property
    def plain(self) -> str:
        r"""
        The plain text without ANSI formatting.
        """
        return super().__str__()

    @cached_property
    def color_only(self) -> str:
        r"""
        The colored text without styles.
        """
        return _assemble_segments(
            self._SEGMENTS,
            use_color=True,
            use_style=False
        )

    @cached_property
    def style_only(self) -> str:
        r"""
        The styled text without colors.
        """
        return _assemble_segments(
            self._SEGMENTS,
            use_color=False,
            use_style=True
        )

    @cached_property
    def rich(self) -> str:
        r"""
        The rich text with colors and styles.
        """
        return _assemble_segments(
            self._SEGMENTS,
            use_color=True,
            use_style=True
        )


def _get_ansi_code(
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


def _assemble_segments(
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
