# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from functools import cached_property
import warnings
from typing import (Any, List, Tuple, Optional, Iterable, Union, Literal)

from ._utils import (get_ansi_code, assemble_segments)
from ..types import (ColorName, StyleName)


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

            NOTE: _ColorName_: `"d"`(black); `"r"`(red); `"g"`(green); `"y"`(yellow); `"b"`(blue); `"m"`(magenta); `"c"`(cyan); `"w"`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable[int]_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

            - `None`: No color applied.

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as parameter :param:`fg`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.

            NOTE: _StyleName_: `"bold"`, `"dim"`, `"italic"`, `"udl"`, `"underline"`, `"blink"`, `"selected"`, `"disappear"`, `"del"`, `"delete"`.

    Returns
    -------
        ColorStr
            The colored string with ANSI escape codes. Usage same as :class:`str`, with `plain`, `color_only`, `style_only` properties. You can combine multiple colored strings using `+` operator or `+=` operator.
    """
    return ColorStr.from_str(text, fg=fg, bg=bg, styles=styles)


class ColorStr(str):
    r"""
    A string class that supports ANSI color and style formatting while preserving plain text.

    NOTE 1: Usage same as :class:`str`, with `plain`, `color_only`, `style_only` properties.

    NOTE 2: The :class:`str` output functions from str class (like :func:`upper()`, :func:`lower()`, etc.) are overridden to preserve color and style formatting for non-combined ColorStr.
    """
    _SEGMENTS: List[Tuple[str, str, str]]  # list of (plain, color_codes, style_codes)
    _CUMSUM: List[int]
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

        Parameter Reference: :func:`ctext()`
        """
        plain = str(_str)
        obj = super().__new__(cls, plain)
        # segments
        if plain and (fg is not None or bg is not None or styles is not None):
            style_code, color_code = get_ansi_code(
                fg=fg,
                bg=bg,
                styles=styles if styles is not None else []
            )
        else:
            style_code = ""
            color_code = ""
        obj._SEGMENTS = [(plain, color_code, style_code)]
        obj._CUMSUM = [len(plain)]
        obj._is_colored = bool(color_code or style_code)

        return obj

    def __new__(
        cls,
        *segments: Tuple[str, str, str]
    ):
        new_segments: List[Tuple[str, str, str]] = []
        last_seg = None
        cumsum: List[int] = [0]

        def _append_last():
            r"""
            Append the last segment to new_segments and update cumsum.
            """
            if last_seg is not None:
                cumsum.append(cumsum[-1] + len(last_seg[0]))
                new_segments.append((last_seg[0], last_seg[1], last_seg[2]))

        is_colored = False
        first_empty = None
        for seg in segments:
            try:
                assert len(seg) == 3
            except Exception:
                warnings.warn(f"Invalid Segment: {seg} Detected When Creating ColorStr.", RuntimeWarning)
                continue
            if seg[1] != "" or seg[2] != "":
                is_colored = True
            str_ = seg[0]
            plain = str_.plain if isinstance(str_, ColorStr) else str(str_)
            if plain:
                if last_seg is None or last_seg[1] != seg[1] or last_seg[2] != seg[2]:
                    # append last segment
                    _append_last()
                    # update
                    last_seg = [plain, seg[1], seg[2]]
                else:
                    # merge with last segment
                    last_seg[0] += plain
            else:
                if first_empty is None:
                    first_empty = seg
        _append_last()

        if len(new_segments) == 0:
            new_segments.append(("", "", "") if first_empty is None else first_empty)
        else:
            cumsum.pop(0)

        obj = super().__new__(cls, assemble_segments(
            new_segments,
            use_color=False,
            use_style=False
        ))
        obj._SEGMENTS = new_segments
        obj._CUMSUM = cumsum
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

    def pieces(self) -> List[ColorStr]:
        r"""
        Segmented into :class:`ColorStr` pieces according to segments.

        Returns
        -------
            List[ColorStr]
                A list of :class:`ColorStr` pieces.
        """
        return [ColorStr(seg) for seg in self._SEGMENTS]

    def del_pieces(self, indices: Iterable[int] = (-1,)) -> ColorStr:
        r"""
        Delete specific segments by their indices.

        Parameters
        ----------
            indices : Iterable[int], default to `(-1,)`
                The indices of segments to be deleted. Negative indices are supported.

        Returns
        -------
            ColorStr
                The colored string with specified segments removed.
        """
        del_set = [idx if idx >= 0 else (len(self._SEGMENTS) + idx) for idx in set(indices)]

        return ColorStr(*[seg for idx, seg in enumerate(self._SEGMENTS) if idx not in del_set])

    def apply(
        self,
        text: Any,
        use_color: bool = True,
        use_style: bool = True,
        _from_left: bool = True,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None,
        segment_idx: Optional[int] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this ColorStr to another :class:`str` from the `left`.

        Parameters
        ----------
            text : Any
                The text content to which the color and style pattern will be applied.

            use_color : bool, default to `True`
                Whether to apply the color codes from the pattern.

            use_style : bool, default to `True`
                Whether to apply the style codes from the pattern.

            start_idx : int, default to `0`
                The starting index from `left` in the text where the pattern will be applied.

            extend : Optional[Literal["left", "right", "all"]], default to `None`
                How to extend the pattern when the text is longer than the pattern.
                - `"left"`: Extend the leftmost segment of the pattern to the left.
                - `"right"`: Extend the rightmost segment of the pattern to the right.
                - `"all"`: Extend both sides.
                - `None`: No extension.

            segment_idx : Optional[int], default to `None`
                If specified, only use the segment at this index from the pattern.

        Returns
        -------
            ColorStr
                The colored string with the applied pattern.

        Raises
        -------
            IndexError
                If :param:`segment_idx` is out of range.
        """
        c_text = text if isinstance(text, ColorStr) else ColorStr.from_str(text)
        # text length
        text_len = len(c_text)
        # pattern
        if segment_idx is None:
            # for all segments
            pattern = self
        else:
            # for specific segment
            try:
                pattern = self.pieces()[segment_idx]
            except IndexError:
                raise IndexError(f"Segment Index {segment_idx} Out Of Range, Must Be 0 <= index < {len(self._SEGMENTS)}.")
        pattern_len = len(pattern)

        if text_len == 0 or pattern_len == 0:
            return c_text

        segments: List[Tuple[str, str, str]] = []
        # determine cut points
        if _from_left:
            pl = start_idx
            pr = start_idx + pattern_len
        else:
            pl = text_len - (start_idx + pattern_len)
            pr = text_len - start_idx
        # left piece
        if pl > 0:
            index = min(pl, text_len)
            if extend in ("left", "all"):
                seg = pattern._SEGMENTS[0]
                segments.append((
                    c_text.plain[0: index],
                    seg[1] if use_color else "",
                    seg[2] if use_style else ""
                ))
            else:
                segments.extend(c_text[0: index]._SEGMENTS)
        # middle piece
        if pl < text_len and pr > 0:
            actual_pattern = pattern[max(-pl, 0): min(pattern_len-(pr-text_len), pattern_len)]
            mid_text = c_text.plain[max(pl, 0): min(pr, text_len)]
            start_idx = 0
            for seg_idx, cum_idx in enumerate(actual_pattern._CUMSUM):
                seg = actual_pattern._SEGMENTS[seg_idx]
                segments.append((
                    mid_text[start_idx: cum_idx],
                    seg[1] if use_color else "",
                    seg[2] if use_style else ""
                ))
                # update
                start_idx = cum_idx
        # right piece
        if pr < text_len:
            index = max(pr, 0)
            if extend in ("right", "all"):
                seg = pattern._SEGMENTS[-1]
                segments.append((
                    c_text.plain[index:],
                    seg[1] if use_color else "",
                    seg[2] if use_style else ""
                ))
            else:
                segments.extend(c_text[index:]._SEGMENTS)

        return ColorStr(*segments)

    def rapply(
        self,
        text: Any,
        use_color: bool = True,
        use_style: bool = True,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None,
        segment_idx: Optional[int] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this ColorStr to another :class:`str` from the `right`.

        Parameter Reference: :func:`apply()`
        """
        return self.apply(
            text=text,
            use_color=use_color,
            use_style=use_style,
            start_idx=start_idx,
            extend=extend,
            segment_idx=segment_idx,
            _from_left=False
        )

    def join(self, iterable: Iterable[Any]) -> ColorStr:
        r"""
        Join an iterable of strings using this :class:`ColorStr` as the separator.

        Parameters
        ----------
            iterable : Iterable[Any]
                An iterable of object to be joined.

        Returns
        -------
            ColorStr
                The joined colored string with ANSI escape codes. Usage same as :class:`str`, with `plain`, `color_only`, `style_only` properties.
        """
        segments = []
        first = True
        for item in iterable:
            if not first:
                segments.extend(self._SEGMENTS)
            first = False
            if isinstance(item, ColorStr):
                segments.extend(item._SEGMENTS)
            else:
                segments.append((str(item), "", ""))
        return ColorStr(*segments)

    
    
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        if callable(attr):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                
                
                
                
                
                if isinstance(result, str) and not isinstance(result, ColorStr) and not self.iscombined():
                    return self.apply(result)
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
            return ColorStr.from_str("")
        return ColorStr(*self._SEGMENTS * n)

    def __getitem__(self, key: Any):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            if step != 1:
                return ColorStr.from_str(super().__getitem__(key))
            # slice segments for non-step slices
            start_idx = 0
            new_segments: List[Tuple[str, str, str]] = []
            for seg_idx, cum_idx in enumerate(self._CUMSUM):
                left_idx = max(start_idx, start)
                right_idx = min(stop, cum_idx)
                if left_idx < right_idx:
                    new_segments.append((
                        self.plain[left_idx: right_idx],
                        self._SEGMENTS[seg_idx][1],
                        self._SEGMENTS[seg_idx][2]
                    ))
                # update
                start_idx = cum_idx
            return ColorStr(*new_segments)
        else:
            return ColorStr.from_str(super().__getitem__(key))

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
        return assemble_segments(
            self._SEGMENTS,
            use_color=True,
            use_style=False
        )

    @cached_property
    def style_only(self) -> str:
        r"""
        The styled text without colors.
        """
        return assemble_segments(
            self._SEGMENTS,
            use_color=False,
            use_style=True
        )

    @cached_property
    def rich(self) -> str:
        r"""
        The rich text with colors and styles.
        """
        return assemble_segments(
            self._SEGMENTS,
            use_color=True,
            use_style=True
        )
