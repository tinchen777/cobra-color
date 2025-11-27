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
    /,
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
) -> ColorStr:
    r"""
    Generate a easy-to-use `rich str` instance with perfect support for :class:`str`, containing `rich str` versions of almost all native :class:`str` features.

    Parameters
    ----------
        text : Any
            The text content.

        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the `rich str`.
            - _ColorName_: `Basic 8 color` OR `Light 8 color`, compatible with older terminals;

            NOTE: _ColorName_: `"d"`(black); `"r"`(red); `"g"`(green); `"y"`(yellow); `"b"`(blue); `"m"`(magenta); `"c"`(cyan); `"w"`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

            - `None`: No color applied.

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the `rich str`.
            (Same format and rules as parameter :param:`fg`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the `rich str`.

            NOTE: _StyleName_: `"bold"`, `"dim"`, `"italic"`, `"udl"`, `"underline"`, `"blink"`, `"selected"`, `"disappear"`, `"del"`, `"delete"`.

    Returns
    -------
        ColorStr
            A :class:`ColorStr` instance with the specified color and style.
    """
    return ColorStr.from_str(text, fg=fg, bg=bg, styles=styles)


def _to_str(obj: Any, default: Optional[str] = None, /) -> str:
    r"""
    Convert an object to :class:`str`, with default value if empty.
    """
    str_ = obj.plain if isinstance(obj, ColorStr) else str(obj)
    if default is None or (default is not None and len(str_) > 0):
        return str_
    else:
        return default.plain if isinstance(default, ColorStr) else str(default)


def _to_ColorStr(obj: Any, default: Optional[str] = None, /) -> ColorStr:
    r"""
    Convert an object to :class:`ColorStr`, with default value if empty.
    """
    c_str = obj if isinstance(obj, ColorStr) else ColorStr.from_str(obj)
    if default is None or (default is not None and len(c_str) > 0):
        return c_str
    else:
        return default if isinstance(default, ColorStr) else ColorStr.from_str(default)


def _fixed_method(func):
    def wrapper(obj: ColorStr):
        try:
            return obj.apply(getattr(obj.plain, func.__name__)())
        except Exception as e:
            raise e.__class__(f"Error When Calling ColorStr.{func.__name__}(): {e}")

    return wrapper


def _extend_method(func):
    def wrapper(obj: ColorStr, width, fillchar=" ", /, extend=None):
        try:
            # width
            if not isinstance(width, int):
                raise TypeError(f"Argument 'width' Must Be An Integer, Got {type(width)}.")
            if width <= len(obj):
                return obj.copy()
            # fillchar
            fillchar = _to_ColorStr(fillchar, " ")
            fillchar_len = len(fillchar)

            left_len, right_len = func(obj, width)
            # left part
            left = fillchar * ((left_len // fillchar_len) + 1)
            # right part
            right = fillchar * ((right_len // fillchar_len) + 1)

            return obj.apply(left[:left_len] + obj + right[:right_len], start_idx=left_len, extend=extend)

        except Exception as e:
            raise e.__class__(f"Error When Calling ColorStr.{func.__name__}({width!r}, {fillchar!r}, extend={extend!r}): {e}")

    return wrapper


def _clip_method(func):
    def wrapper(obj: ColorStr, *args):
        try:
            str_result = getattr(obj.plain, func.__name__)(*args)
            return obj.apply(str_result, start_idx=-obj.find(str_result))
        except Exception as e:
            args = ", ".join([repr(arg) for arg in args])
            raise e.__class__(f"Error When Calling ColorStr.{func.__name__}({args}): {e}")

    return wrapper


class ColorStr(str):
    r"""
    An easy-to-use `rich str` class with perfect support for :class:`str`, containing `rich str` versions of almost all native :class:`str` features.
    """
    _SEGMENTS: List[Tuple[str, str, str]]  # list of (plain, color_codes, style_codes)
    _CUMSUM: List[int]
    _is_colored: bool

    @classmethod
    def from_str(
        cls,
        str_: Any,
        /,
        fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
        styles: Optional[Iterable[StyleName]] = None
    ):
        r"""
        Create a :class:`ColorStr` instance from a regular string with specified color and style.

        Parameter Reference: :func:`ctext()`
        """
        plain = str(str_)
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
            str_ = _to_str(seg[0])
            if str_:
                if last_seg is None or last_seg[1] != seg[1] or last_seg[2] != seg[2]:
                    # append last segment
                    _append_last()
                    # update
                    last_seg = [str_, seg[1], seg[2]]
                else:
                    # merge with last segment
                    last_seg[0] += str_
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

    def to(
        self,
        use_color: bool = True,
        use_style: bool = True
    ) -> ColorStr:
        r"""
        Create a new :class:`ColorStr` instance with specified color and style usage from the current :class:`ColorStr`.

        Parameters
        ----------
            use_color : bool, default to `True`
                Whether to keep the color codes.

            use_style : bool, default to `True`
                Whether to keep the style codes.

        Returns
        -------
            ColorStr
                A new :class:`ColorStr` instance with specified color and style usage.
        """
        return ColorStr(*[
            (seg[0], seg[1] if use_color else "", seg[2] if use_style else "")
            for seg in self._SEGMENTS
        ])

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

    def del_pieces(self, indices: Iterable[int] = (-1,), /) -> ColorStr:
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
        /,
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
        c_text = _to_ColorStr(text)
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

        # check start_idx
        if not isinstance(start_idx, int):
            raise TypeError(f"[ColorStr.apply()] Argument 'start_idx' Must Be An Integer, Got {type(start_idx)}.")

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
                    c_text.plain[0: index], seg[1], seg[2]))
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
                    mid_text[start_idx: cum_idx], seg[1], seg[2]))
                # update
                start_idx = cum_idx
        # right piece
        if pr < text_len:
            index = max(pr, 0)
            if extend in ("right", "all"):
                seg = pattern._SEGMENTS[-1]
                segments.append((
                    c_text.plain[index:], seg[1], seg[2]))
            else:
                segments.extend(c_text[index:]._SEGMENTS)

        return ColorStr(*segments)

    def rapply(
        self,
        text: Any,
        /,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None,
        segment_idx: Optional[int] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this ColorStr to another :class:`str` from the `right`.

        Parameter Reference: :func:`apply()`
        """
        return self.apply(
            text,
            start_idx=start_idx,
            extend=extend,
            segment_idx=segment_idx,
            _from_left=False
        )

    def join(self, iterable: Iterable[Any], /) -> ColorStr:
        r"""
        Join an iterable of strings using this :class:`ColorStr` as the separator.

        Parameters
        ----------
            iterable : Iterable[Any]
                An iterable of object to be joined.

        Returns
        -------
            ColorStr
                The joined :class:`ColorStr`.
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

    def split(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep = _to_str(sep, " ")

        result: List[ColorStr] = []
        count = 0
        start_idx = 0
        end_idx = -1
        while maxsplit == -1 or count < maxsplit:
            end_idx = self.find(sep, start_idx)
            if end_idx == -1:
                break
            # segment
            result.append(self[start_idx: end_idx])
            # update
            start_idx = end_idx + len(sep)
            count += 1
        # last segment
        result.append(self[start_idx:])

        return result

    def rsplit(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep = _to_str(sep, " ")

        result: List[ColorStr] = []
        count = 0
        end_idx = len(self)
        start_idx = -1
        while maxsplit == -1 or count < maxsplit:
            start_idx = self.rfind(sep, 0, end_idx)
            if start_idx == -1:
                break
            # segment
            result.append(self[start_idx + len(sep): end_idx])
            # update
            end_idx = start_idx
            count += 1
        # last segment
        result.append(self[0: end_idx])
        result.reverse()

        return result

    def splitlines(self, keepends: bool = False) -> List[ColorStr]:  # type: ignore[misc]
        result = self.split("\n")
        if keepends:
            for i in range(len(result) - 1):
                result[i] += "\n"
        return result

    def partition(self, sep: Any) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        sep = _to_str(sep)

        idx = self.find(sep)
        if idx == -1:
            return (self.copy(), ColorStr.from_str(""), ColorStr.from_str(""))
        else:
            return (
                self[0: idx],
                self[idx: idx + len(sep)],
                self[idx + len(sep):]
            )

    def rpartition(self, sep: Any) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        sep = _to_str(sep)

        idx = self.rfind(sep)
        if idx == -1:
            return (ColorStr.from_str(""), ColorStr.from_str(""), self.copy())
        else:
            return (
                self[0: idx],
                self[idx: idx + len(sep)],
                self[idx + len(sep):]
            )

    def replace(self, old: str, new: str, /, count: Any = -1) -> ColorStr:
        old = _to_str(old)  # old must be str
        new = _to_ColorStr(new)

        return new.join(self.split(old, maxsplit=count))

    @_fixed_method
    def capitalize(self) -> ColorStr: ...

    @_fixed_method
    def casefold(self) -> ColorStr: ...

    @_fixed_method
    def lower(self) -> ColorStr: ...

    @_fixed_method
    def swapcase(self) -> ColorStr: ...

    @_fixed_method
    def title(self) -> ColorStr: ...

    @_fixed_method
    def upper(self) -> ColorStr: ...

    @_extend_method
    def center(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        padding = width - len(self)
        left = padding // 2 + (padding % 2)
        right = padding // 2

        return left, right  # type: ignore

    @_extend_method
    def ljust(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["right"]] = None
    ) -> ColorStr:
        return 0, width - len(self)  # type: ignore

    @_extend_method
    def rjust(
        self,
        width: Any,
        fillchar: str = " ",
        /,
        extend: Optional[Literal["left"]] = None
    ) -> ColorStr:
        return width - len(self), 0  # type: ignore

    def zfill(
        self,
        width: Any,
        /,
        extend: Optional[Literal["left"]] = None
    ) -> ColorStr:
        return self.rjust(width, "0", extend=extend)

    @_clip_method
    def strip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def lstrip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def rstrip(self, chars: str | None = None, /) -> ColorStr: ...

    @_clip_method
    def removeprefix(self, prefix: str, /) -> ColorStr: ...

    @_clip_method
    def removesuffix(self, suffix: str, /) -> ColorStr: ...

    def copy(self):
        r"""
        Create a copy of the :class:`ColorStr`.
        """
        return ColorStr(*self._SEGMENTS)

    def __add__(self, other_str: str, /):
        if isinstance(other_str, ColorStr):
            other_segments = other_str._SEGMENTS
        else:
            other_segments = [(str(other_str), "", "")]
        return ColorStr(*(self._SEGMENTS + other_segments))

    def __mul__(self, n: Any, /):
        assert isinstance(n, int), "Can Only Multiply ColorStr By An Integer."
        if n <= 0:
            return ColorStr.from_str("")
        return ColorStr(*self._SEGMENTS * n)

    def __getitem__(self, key: Any, /):
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
                if left_idx <= right_idx:
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
