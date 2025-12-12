# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from functools import (cached_property, wraps)
from typing import (Any, List, Tuple, Set, Optional, Sequence, Iterable, Literal, Union, final, overload)

from ._extension import (ExtStr, to_ExtStr)
from ._segment import (ColorSeg, ansi_to_segments)
from ._utils import (wrap_exc, to_fgcode, to_bgcode, to_style_codes)
from ..types import (T_ColorSpec, T_StyleName)


def _to_plain(obj: Any, default: Optional[str] = None, /) -> ExtStr:
    r"""
    Convert an object to :class:`ExtStr`, with default value if empty.
    """
    plain = obj.plain if isinstance(obj, ColorStr) else to_ExtStr(obj)
    if default is not None and len(plain) == 0:
        return default.plain if isinstance(default, ColorStr) else to_ExtStr(default)
    else:
        return plain


def _to_ColorStr(obj: Any, default: Optional[str] = None, /) -> ColorStr:
    r"""
    Convert an object to :class:`ColorStr`, with default value if empty.
    """
    c_str = obj if isinstance(obj, ColorStr) else ColorStr.from_str(obj)
    if default is not None and len(c_str) == 0:
        return default if isinstance(default, ColorStr) else ColorStr.from_str(default)
    else:
        return c_str


@overload
def ctext(ansi: Any, /) -> ColorStr: ...


@overload
def ctext(
    text: Any,
    /,
    fg: Optional[T_ColorSpec] = None,
    bg: Optional[T_ColorSpec] = None,
    styles: Optional[Iterable[T_StyleName]] = None
) -> ColorStr: ...


def ctext(
    text: Any,
    /,
    fg: Optional[T_ColorSpec] = None,
    bg: Optional[T_ColorSpec] = None,
    styles: Optional[Iterable[T_StyleName]] = None
) -> ColorStr:
    r"""
    Generate an easy-to-use :class:`ColorStr` instance, `rich str`, with perfect support for :class:`str`, containing :class:`ColorStr` versions of almost all native :class:`str` features.

    Parameters
    ----------
        text : Any
            The text content or ANSI formatted text content.

        fg : Optional[ColorSpec], default to `None`
            The foreground color of the `rich str`.
            - _ColorName_: `Basic 8 color` OR `Light 8 color`, compatible with older terminals;

            NOTE: _ColorName_: `"d"`(black); `"r"`(red); `"g"`(green); `"y"`(yellow); `"b"`(blue); `"m"`(magenta); `"c"`(cyan); `"w"`(white). Prefix `l` means Light 8 color.

            - _int_: `256 color`, compatible with most terminals;

            NOTE: `0-7`: Basic 8 color; `8-15`: Light 8 color; `16-231`: 6x6x6 color cube; `232-255`: grayscale from dark to light.

            - _Iterable_: `True color`, compatible with modern terminals.

            NOTE: Each value should be in range `0-255`, representing `R`, `G`, `B` respectively.

            - `None`: No color applied.

        bg : Optional[ColorSpec], default to `None`
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


@overload
def to_ansi(text: Any, /) -> ExtStr: ...


@overload
def to_ansi(
    text: Any,
    /,
    fg: Optional[T_ColorSpec] = None,
    bg: Optional[T_ColorSpec] = None,
    styles: Optional[Iterable[T_StyleName]] = None
) -> ExtStr: ...


def to_ansi(
    text: Any,
    /,
    fg: Optional[T_ColorSpec] = None,
    bg: Optional[T_ColorSpec] = None,
    styles: Optional[Iterable[T_StyleName]] = None
) -> ExtStr:
    r"""
    Convert an object to an ANSI formatted :class:`ExtStr` with specified color and style.
    Parameter Reference: :func:`ctext()`

    Returns
    -------
        ExtStr
            An ANSI formatted :class:`ExtStr` instance.
    """
    if fg is None and bg is None and styles is None:
        return _to_plain(text)
    return ColorSeg.from_raw(_to_plain(text), fg=fg, bg=bg, styles=styles).to_str()


@wrap_exc
def _fixed_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr):
        return obj.apply(getattr(obj.plain, func.__name__)())
    return wrapper


@wrap_exc
def _extend_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr, width, fillchar=" ", /, extend=None):
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
    return wrapper


@wrap_exc
def _clip_method(func):
    @wraps(func)
    def wrapper(obj: ColorStr, *args):
        str_result = getattr(obj.plain, func.__name__)(*args)
        return obj.apply(str_result, start_idx=-obj.find(str_result))
    return wrapper


@final
class ColorStr(ExtStr):
    r"""
    An easy-to-use `rich str` with perfect support for :class:`str`, containing :class:`ColorStr` versions of almost all native :class:`str` features.
    """
    _SEGMENTS: List[ColorSeg]
    _plain: ExtStr

    @classmethod
    def from_str(
        cls,
        str_: Any,
        /,
        fg: Optional[T_ColorSpec] = None,
        bg: Optional[T_ColorSpec] = None,
        styles: Optional[Iterable[T_StyleName]] = None
    ):
        r"""
        Create a :class:`ColorStr` instance from an ANSI formatted string.
        Parameter Reference: :func:`ctext()`
        """
        if fg is None and bg is None and styles is None:
            return cls(*ansi_to_segments(_to_plain(str_)), copy=False)
        return cls(ColorSeg.from_raw(_to_plain(str_), fg=fg, bg=bg, styles=styles), copy=False)

    def __new__(cls, *segments: ColorSeg, copy: bool = True):
        r"""
        Create a :class:`ColorStr` instance from :class:`ColorSeg` instances.
        """
        if len(segments) == 0:
            # no segments provided
            new_segments = [ColorSeg.empty()]
        else:
            # segments provided
            new_segments = [segments[0].copy() if copy else segments[0]]
            new_segments[-1].set_istart(0)
            for seg in segments[1:]:
                if seg.plain:
                    if seg.isequal(new_segments[-1], ("fg", "bg", "styles")):
                        # merge with last segment
                        new_segments[-1]._update_plain(seg.plain, mode="+=")
                    else:
                        # append new segment
                        seg = seg.copy() if copy else seg
                        seg.set_istart(new_segments[-1].iend)
                        new_segments.append(seg)

        plain = ExtStr.from_iter(seg.plain for seg in new_segments)
        obj = super().__new__(cls, plain)
        obj._is_fg_colored = any(seg.isfgcolored for seg in new_segments)
        obj._is_bg_colored = any(seg.isbgcolored for seg in new_segments)
        obj._is_styled = any(seg.isstyled for seg in new_segments)
        obj._SEGMENTS = new_segments
        obj._plain = plain

        return obj

    def recolor(
        self,
        apply_range: Optional[slice] = None,
        /,
        fg: Optional[Union[Sequence[Tuple[Any, Any]], str]] = None,
        bg: Optional[Union[Sequence[Tuple[Any, Any]], str]] = None,
        styles: Optional[Union[Sequence[Tuple[Any, Any]], Set[str]]] = None
    ):
        r"""
        Recolor and restyle the :class:`ColorStr` according to the specified mapping rules.

        Parameters
        ----------
            apply_range : Optional[slice], default to `None`
                The range to which the recoloring and restyling will be applied.
                - `None`: Apply to the entire :class:`ColorStr`.
                - `slice`: A slice object defining the range.

            fg : Optional[Union[Sequence[Tuple[Any, Any]], str]], default to `None`
                The `mapping pairs` or `single value` for foreground color replacement.
                - `None`: No change.
                - If a `single value` is provided, all segments' foreground color will be replaced with the specified value.
                - If a sequence of `mapping pairs` is provided, each pair defines a mapping from _key_ to _value_.

                For each mapping _key_:
                - _ColorSpec_: Reference to :type:`ColorSpec`;
                - `""`: Match segments without foreground color.

                For each mapping _value_:
                - _ColorSpec_: Reference to :type:`ColorSpec`;
                - `""`: Remove the foreground color.

            bg : Optional[Union[Sequence[Tuple[Any, Any]], str]], default to `None`
                The `mapping pairs` or `single value` for background color replacement.
                (Same format and rules as parameter :param:`fg`)

            styles : Optional[Union[Sequence[Tuple[Any, Any]], Set[str]]], default to `None`
                The `mapping pairs` or `single value` for style replacement.
                - `None`: No change.
                - If a `single value` is provided, all segments' styles will be replaced with the specified styles.
                - If a sequence of `mapping pairs` is provided, each pair defines a mapping from _key_ to _value_.

                For each mapping _key_:
                - `Set[StyleName]`: A set of styles to match;
                - `"all"`: Match all segments;
                - `None`: No match, add new styles to all segments.

                For each mapping _value_:
                - `Set[StyleName]`: A set of styles to apply;
                - `None`: Remove matched styles.

                NOTE: For style mapping, the key is a set of styles. If all styles in the key set are present in the segment, they will be replaced.

        Returns
        -------
            ColorStr
                The recolored and restyled :class:`ColorStr`.
        """
        # foreground mapping
        if fg is not None:
            to_fg = lambda x: "" if x == "" else to_fgcode(x)
            if isinstance(fg, Sequence) and not isinstance(fg, str):
                fg = [(to_fg(k), to_fg(v)) for k, v in fg]
            else:
                fg = to_fg(fg)
        # background mapping
        if bg is not None:
            to_bg = lambda x: "" if x == "" else to_bgcode(x)
            if isinstance(bg, Sequence) and not isinstance(bg, str):
                bg = [(to_bg(k), to_bg(v)) for k, v in bg]
            else:
                bg = to_bg(bg)
        # styles mapping
        if styles is not None:
            to_style = lambda x: None if x is None else to_style_codes(x)
            if isinstance(styles, Sequence) and not isinstance(styles, str):
                styles = [(to_style(k), to_style(v)) for k, v in styles]
            else:
                styles = [("all", to_style(styles))]
        # rebuild
        if apply_range is None:
            apply_range = slice(0, len(self))
        start, stop, _ = self._loc(apply_range)
        sub_ = self[start: stop]
        for seg in sub_._SEGMENTS:
            seg._update(fg=fg, bg=bg, styles=styles)

        return self.insert(start, sub_, overwrite=True)

    def pieces(self) -> List[ColorStr]:
        r"""
        Segmented into :class:`ColorStr` pieces according to segments.

        Returns
        -------
            List[ColorStr]
                A list of :class:`ColorStr` pieces.
        """
        return [ColorStr(seg) for seg in self._SEGMENTS]

    def apply(
        self,
        text: Any,
        /,
        _from_left: bool = True,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this :class:`ColorStr` to another :class:`str` from the `left`.

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

        Returns
        -------
            ColorStr
                The colored string with the applied pattern.
        """
        c_text = _to_ColorStr(text)
        # text length
        text_len = len(c_text)
        if text_len == 0:
            return c_text
        # check start_idx
        if not isinstance(start_idx, int):
            raise TypeError(f"[ColorStr.apply()] Argument 'start_idx' Must Be An Integer, Got {type(start_idx)}.")
        # pattern
        src_str_len = len(self)
        if _from_left:
            pl = start_idx
            pr = pl + src_str_len
        else:
            pr = text_len - start_idx
            pl = pr - src_str_len
        pattern = self[
            max(-pl, 0): min(src_str_len-(pr-text_len), src_str_len)
        ]._SEGMENTS

        new_segments: List[ColorSeg] = []
        # left piece
        if pl > 0:
            if extend in ("left", "all"):
                new_segments.append(pattern[0](c_text.plain[0: pl]))
            else:
                new_segments.extend(c_text[0: pl]._SEGMENTS)
        # middle piece
        if pl < text_len and pr > 0:
            mid_text = c_text.plain[max(pl, 0): pr]
            for seg in pattern:
                new_segments.append(seg(mid_text[seg.istart: seg.iend]))
        # right piece
        if pr < text_len:
            index = max(pr, 0)
            if extend in ("right", "all"):
                new_segments.append(pattern[-1](c_text.plain[index:]))
            else:
                new_segments.extend(c_text[index:]._SEGMENTS)

        return ColorStr(*new_segments, copy=False)

    def rapply(
        self,
        text: Any,
        /,
        start_idx: int = 0,
        extend: Optional[Literal["left", "right", "all"]] = None
    ) -> ColorStr:
        r"""
        Apply the color and style pattern of this :class:`ColorStr` to another :class:`str` from the `right`.

        Parameter Reference: :func:`apply()`
        """
        return self.apply(text, start_idx=start_idx, extend=extend, _from_left=False)

    def findall(
        self,
        sub: Any,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1,
        _reverse: bool = False
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ColorStr`.
        """
        if isinstance(sub, ColorStr) and not sub.isplain:
            # for ColorStr
            sub_len = len(sub)
            if _reverse:
                all_locs = self.plain.rfindall(sub.plain, start, end)
                all_locs.reverse()
            else:
                all_locs = self.plain.findall(sub.plain, start, end)
            result: List[int] = []
            count = 0
            for start_idx in all_locs:
                if sub == self[start_idx: start_idx + sub_len]:
                    result.append(start_idx)
                    count += 1
                    if maxsplit != -1 and count >= maxsplit:
                        break
            if _reverse:
                result.reverse()
            return result
        else:
            # for non-ColorStr
            if _reverse:
                return self.plain.rfindall(sub, start, end, maxsplit=maxsplit)
            else:
                return self.plain.findall(sub, start, end, maxsplit=maxsplit)

    def rfindall(
        self,
        sub: Any,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ColorStr` in reverse order.
        """
        return self.findall(sub, start, end, maxsplit=maxsplit, _reverse=True)

    def find(self, sub: Any, /, start: int = 0, end: Optional[int] = None) -> int:  # type: ignore
        idx_list = self.findall(sub, start, end, maxsplit=1)
        return idx_list[0] if idx_list else -1

    def rfind(self, sub: Any, /, start: int = 0, end: Optional[int] = None) -> int:  # type: ignore
        idx_list = self.rfindall(sub, start, end, maxsplit=1)
        return idx_list[0] if idx_list else -1

    def join(self, iterable: Iterable[Any], /) -> ColorStr:
        segments: List[ColorSeg] = []
        first = True
        for item in iterable:
            if not first:
                segments.extend(self._SEGMENTS)
            first = False
            segments.extend(_to_ColorStr(item)._SEGMENTS)
        return ColorStr(*segments)

    def split(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        new_segments: List[ColorStr] = []
        count = 0
        start_idx = 0
        end_idx = -1
        while maxsplit == -1 or count < maxsplit:
            end_idx = self.find(sep_, start_idx)
            if end_idx == -1:
                break
            # segment
            new_segments.append(self[start_idx: end_idx])
            # update
            start_idx = end_idx + len(sep_)
            count += 1
        # last segment
        new_segments.append(self[start_idx:])

        return new_segments

    def rsplit(self, sep: Any = " ", /, maxsplit: int = -1) -> List[ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        new_segments: List[ColorStr] = []
        count = 0
        end_idx = len(self)
        start_idx = -1
        while maxsplit == -1 or count < maxsplit:
            start_idx = self.rfind(sep_, 0, end_idx)
            if start_idx == -1:
                break
            # segment
            new_segments.append(self[start_idx + len(sep_): end_idx])
            # update
            end_idx = start_idx
            count += 1
        # last segment
        new_segments.append(self[0: end_idx])
        new_segments.reverse()

        return new_segments

    def splitlines(self, keepends: bool = False) -> List[ColorStr]:  # type: ignore[misc]
        result = self.split("\n")
        if keepends:
            for i in range(len(result) - 1):
                result[i] += "\n"
        return result

    def partition(self, sep: Any, /, _reverse: bool = False) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        sep_ = to_ExtStr(sep)
        idx = self.rfind(sep_) if _reverse else self.find(sep_)
        if idx == -1:
            if _reverse:
                return (ColorStr(), ColorStr(), self.copy())
            else:
                return (self.copy(), ColorStr(), ColorStr())
        else:
            return (
                self[0: idx],
                self[idx: idx + len(sep_)],
                self[idx + len(sep_):]
            )

    def rpartition(self, sep: Any, /) -> Tuple[ColorStr, ColorStr, ColorStr]:  # type: ignore
        return self.partition(sep, _reverse=True)

    def replace(self, old: Any, new: Any, /, count: Any = -1) -> ColorStr:
        return _to_ColorStr(new).join(self.split(old, maxsplit=count))

    def insert(
        self,
        index: int,
        sub: Any,
        /,
        overwrite: bool = False,
        keep_pattern: bool = True
    ) -> ColorStr:
        r"""
        Insert a substring into the :class:`ColorStr` at the specified index.

        Parameters
        ----------
            index : int
                The index at which to insert the substring.

            sub : Any
                The substring to insert.

            overwrite : bool, default to `False`
                Whether to overwrite existing content at the insertion point.

            keep_pattern : bool, default to `True`
                Whether to keep the original pattern of the string.

        Returns
        -------
            ColorStr
                The new :class:`ColorStr` with the substring inserted.
        """
        index = self._loc(index)
        sub_ = _to_ColorStr(sub)
        if not keep_pattern:
            if overwrite:
                sub_ = self.apply(sub_, start_idx=-index)
            else:
                sub_ = self[index].apply(sub_, extend="all")

        if overwrite:
            return self[0: index] + sub_ + self[index + len(sub_):]
        return self[0: index] + sub_ + self[index:]

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

    @overload
    def _loc(self, s: slice, /) -> Tuple[int, int, int]: ...

    @overload
    def _loc(self, idx: int, /) -> int: ...

    @overload
    def _loc(self, start: int, end: int, /) -> Tuple[int, int]: ...

    def _loc(self, start: Union[slice, int], end: Optional[int] = None, /):
        r"""
        Get the valid start and end indices for slicing.
        """
        # slice
        if isinstance(start, slice):
            start_idx, end_idx, step = start.indices(len(self))
            return start_idx, end_idx, step
        # single index
        if end is None:
            if start < 0:
                start += len(self)
            if start < 0 or start >= len(self):
                raise IndexError(f"ColorStr Index:{start} Out Of Range:[-{len(self)}, {len(self)}).")
            return start
        # slice indices
        start_idx, end_idx, _ = slice(start, end).indices(len(self))
        return start_idx, end_idx

    def __call__(self, text: Any, /) -> ColorStr:
        return self.apply(text)

    def __add__(self, other: Any, /):
        return ColorStr(*(self._SEGMENTS + _to_ColorStr(other)._SEGMENTS))

    def __mul__(self, n: Any, /):
        assert isinstance(n, int), "Can Only Multiply ColorStr By An Integer."
        if n <= 0:
            return ColorStr()
        return ColorStr(*[seg for _ in range(n) for seg in self._SEGMENTS])

    def __eq__(self, value: Any, /):
        if isinstance(value, str):
            val = to_ExtStr(value)
            if self.isplain and val.isplain:
                # self isplain, value isplain
                return super().__eq__(value)
            elif not self.isplain and not val.isplain and isinstance(val, ColorStr):
                # self iscolored, value iscolored
                return self._SEGMENTS == val._SEGMENTS
        return False

    def __ne__(self, value: Any, /):
        return not self.__eq__(value)

    def __contains__(self, value: Any, /):
        return self.find(value) != -1

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, key: Any, /):
        if isinstance(key, slice):
            start, stop, step = self._loc(key)
            if step != 1:
                return ColorStr.from_str(super().__getitem__(key))
            # slice segments for non-step slices
            new_segments: List[ColorSeg] = []
            for seg in self._SEGMENTS:
                if start >= seg.iend or stop <= seg.istart:
                    continue
                left_idx = max(seg.istart, start)
                right_idx = min(stop, seg.iend)
                if left_idx <= right_idx:
                    new_segments.append(seg(self.plain[left_idx: right_idx]))
            return ColorStr(*new_segments, copy=False)
        elif isinstance(key, int):
            key = self._loc(key)
            # find segment
            for seg in self._SEGMENTS:
                if seg.istart <= key < seg.iend:
                    return ColorStr(seg(self.plain[key]), copy=False)
            # should not reach here
            raise IndexError("ColorStr Index Out Of Range")
        else:
            return ColorStr.from_str(super().__getitem__(key))

    def __str__(self):
        return self.rich

    def __repr__(self):
        return repr(self.rich)

    @property
    def iscombined(self) -> bool:
        r"""
        Check if the :class:`ColorStr` is combined from multiple segments.
        """
        return len(self._SEGMENTS) > 1

    @property
    def plain(self) -> ExtStr:
        r"""
        The plain :class:`ExtStr` string without any color or style.
        """
        return self._plain

    @cached_property
    def rich(self) -> ExtStr:
        r"""
        The rich text with colors and styles.
        """
        return ExtStr.from_iter(seg.to_str() for seg in self._SEGMENTS)
