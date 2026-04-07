# src/cobra_color/types.py
"""
Type definitions for :pkg:`cobra_color` package.
"""

from __future__ import annotations
from typing import (Sequence, Union, Literal, Optional, Tuple, Set, Iterable)

ColorName = Literal["d", "r", "g", "y", "b", "m", "c", "w", "ld", "lr", "lg", "ly", "lb", "lm", "lc", "lw"]
ColorSpec = Union[ColorName, int, Sequence[int]]
"""
`(Color Specification Type)`. Includes one of the following:

- _ColorName_: A `Basic 8 color` OR `Light 8 color` name, compatible with older terminals;

    NOTE: _ColorName_: `"d"`(black); `"r"`(red); `"g"`(green); `"y"`(yellow); `"b"`(blue); `"m"`(magenta); `"c"`(cyan); `"w"`(white). Prefix `l` means Light 8 color.
- _int_: A `256 color` number, compatible with most terminals;

    NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.
- _Sequence(int)_: A `True color` sequence, compatible with modern terminals.

    NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.
"""
ColorMatch = Optional[Union[str, int, Sequence[int]]]
ColorTrans = Tuple[Optional[str], Optional[str]]
ColorDesc = Union[ColorSpec, Sequence[Tuple[ColorMatch, ColorMatch]]]

StyleName = Literal["bold", "dim", "italic", "udl", "underline", "blink", "selected", "disappear", "del", "delete"]
StyleSpec = Union[StyleName, str, Iterable[str]]
"""
`(Style Specification Type)`. Includes one of the following:

- _StyleName_: A `Text style` name;

    NOTE: _StyleName_: `"bold"`, `"dim"`, `"italic"`, `"udl"`, `"underline"`, `"blink"`, `"selected"`, `"disappear"`, `"del"`, `"delete"`.
- _str_: A `style code` number;

    NOTE: _style_code_: `"1"`(bold), `"2"`(dim), `"3"`(italic), `"4"`(underline/udl), `"5"`(blink), `"7"`(selected), `"8"`(disappear), `"9"`(delete/del).

- _Iterable(str)_: An iterable of `Text style` names OR `style code` numbers.
"""
StyleMatch = Optional[Union[str, Iterable[str]]]
StyleTrans = Tuple[Optional[Union[Set[str], Literal["all"]]], Optional[Set[str]]]
StyleDesc = Union[StyleSpec, Sequence[Tuple[StyleMatch, StyleMatch]]]

ImgFillingMode = Literal["ascii", "color", "half-color", "gray", "half-gray"]
ImgBlockFillingMode = Literal["color", "half-color", "gray", "half-gray"]
