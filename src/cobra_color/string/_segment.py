# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
import warnings
from typing import (Union, Optional, Sequence, Iterable, Dict, Tuple, Set, List, Any, Literal, final)

from ._utils import (
    __ANSI_RE,
    __STYLE_CODE,
    _fmt_ansicolor,
    to_fgcode,
    to_bgcode,
    to_style_codes
)
from ._extension import (to_ExtStr, ExtStr)
from ..types import (T_ColorSpec, T_ColorTrans, T_StyleName, T_StyleModTarget, T_StyleTrans)


def ansi_to_segments(ansi: str, /):
    r"""
    Parse an ANSI formatted string into a list of :class:`ColorSeg` segments.
    """
    segments: List[ColorSeg] = []
    last_idx = 0
    cur_fg = cur_bg = ""
    cur_styles: Set[str] = set()
    for m in __ANSI_RE.finditer(ansi):
        start, end = m.span()
        # text before ANSI code
        if start > last_idx:
            segments.append(ColorSeg(ansi[last_idx: start], cur_fg, cur_bg, cur_styles))
        # ANSI code
        code_iter = iter(m.group(1).split(';'))  # e.g.: "1;31;44"
        for code in code_iter:
            if code == "0" or code == "":
                # reset all
                cur_fg = cur_bg = ""
                cur_styles = set()
            elif code in __STYLE_CODE:
                # style code
                cur_styles.add(code)
            else:
                fg, bg = _fmt_ansicolor(code_iter, c_code=code)
                cur_fg = fg or cur_fg
                cur_bg = bg or cur_bg
        last_idx = end
    if last_idx < len(ansi):
        segments.append(ColorSeg(ansi[last_idx:], cur_fg, cur_bg, cur_styles))

    return segments


@final
class ColorSeg:
    r"""
    A segment of color and style information for :class:`ColorStr`.
    """
    _START_IDX: int

    @classmethod
    def from_raw(
        cls,
        str_: Any,
        /,
        fg: Optional[T_ColorSpec] = None,
        bg: Optional[T_ColorSpec] = None,
        styles: Optional[Iterable[T_StyleName]] = None
    ):
        r"""
        Create a :class:`ColorSeg` instance from a string with specified color and style.
        """
        return cls(
            str_,
            fg_code=to_fgcode(fg) or "",
            bg_code=to_bgcode(bg) or "",
            style_codes=to_style_codes(styles)
        )

    @classmethod
    def empty(cls):
        r"""
        Create an empty :class:`ColorSeg` instance.
        """
        return cls("", fg_code="", bg_code="", style_codes=set())

    def __init__(
        self,
        plain: str,
        /,
        fg_code: str,
        bg_code: str,
        style_codes: Iterable[str]
    ):
        self._plain = to_ExtStr(plain)
        self._fg_code = fg_code
        self._bg_code = bg_code
        # style_codes
        try:
            self._style_codes = set(style_codes)
            self._style_codes.discard("")
        except TypeError:
            raise TypeError("`style_codes` Of Class[ColorSeg] Must Be An Iterable Of Style Names.")
        # init start index
        self._START_IDX = 0

    def isequal(
        self,
        other: Any,
        /,
        flags: Tuple[Literal["plain", "fg", "bg", "styles"], ...] = ("plain", "fg", "bg", "styles")
    ) -> bool:
        r"""
        Compare with another :class:`ColorSeg` for equality based on specified attributes.

        Parameters
        ----------
            other : ColorSeg
                The other :class:`ColorSeg` instance to compare with.

            flags : Tuple[Literal["plain", "fg", "bg", "styles"], ...], default to `("plain", "fg", "bg", "styles")`
                The attributes to consider for comparison.

        Returns
        -------
            bool
        """
        if not isinstance(other, ColorSeg):
            return False

        if "plain" in flags and self.plain != other.plain:
            return False
        if "fg" in flags and self.fg != other.fg:
            return False
        if "bg" in flags and self.bg != other.bg:
            return False
        if "styles" in flags and self.styles != other.styles:
            return False
        return True

    def assemble(self, *enable: Literal["fg", "bg", "styles"]) -> ExtStr:
        r"""
        Assemble the :class:`ColorSeg` into an ANSI formatted string based on specified attributes.
        """
        if not self.plain:
            return to_ExtStr("")
        styles = ";".join(self.styles) if "styles" in enable else ""
        fg = f";{self.fg}" if "fg" in enable and self.fg else ""
        bg = f";{self.bg}" if "bg" in enable and self.bg else ""
        codes = f"{styles}{fg}{bg}"
        if codes:
            return to_ExtStr(f"\033[{codes}m{self.plain}\033[0m")
        return self.plain

    def copy(self, istart: Optional[int] = None) -> ColorSeg:
        r"""
        Create a copy of the :class:`ColorSeg` instance.
        """
        new_seg = ColorSeg(
            self.plain,
            fg_code=self.fg,
            bg_code=self.bg,
            style_codes=self.styles
        )
        new_seg.set_istart(self._START_IDX if istart is None else istart)
        return new_seg

    def set_istart(self, idx: Any, /):
        r"""
        Set the start index of the :class:`ColorSeg` in the original string.
        """
        if isinstance(idx, int) and idx >= 0:
            self._START_IDX = idx

    def apply(self, text: str, /) -> ColorSeg:
        r"""
        Apply the color and style of the :class:`ColorSeg` instance to a new string.

        Parameters
        ----------
            text : str
                The new string to apply the color and style to.

        Returns
        -------
            ColorSeg
                A new :class:`ColorSeg` instance with the applied string.
        """
        return ColorSeg(text, self.fg, self.bg, self.styles)

    def to_str(self) -> ExtStr:
        r"""
        Covert the :class:`ColorSeg` instance to an ANSI formatted string.
        """
        return self.assemble("fg", "bg", "styles")

    def _update_plain(self, target: Any, /, mode: Literal["=", "+="]):
        r"""
        Modify the plain string of the :class:`ColorSeg` instance.
        """
        if target is not None:
            if mode == "=":
                self._plain = to_ExtStr(target)
            elif mode == "+=":
                self._plain += to_ExtStr(target)
            else:
                raise ValueError(f"Invalid Mode For ColorSeg._update_plain(), Mode: {mode}.")

    def _update_fg(self, target: Optional[str], to: Optional[str], /):
        r"""
        Replace the foreground color of the :class:`ColorSeg` instance.
        """
        if target is not None and to is not None and self.fg == target:
            self._fg_code = to

    def _update_bg(self, target: Optional[str], to: Optional[str], /):
        r"""
        Replace the background color of the :class:`ColorSeg` instance.
        """
        if target is not None and to is not None and self.bg == target:
            self._bg_code = to

    def _update_styles(
        self,
        target: Optional[T_StyleModTarget],
        to: Optional[Set[str]],
        /
    ):
        r"""
        Modify the styles of the :class:`ColorSeg` instance.
        """
        if target == "all":
            # modify all styles
            if to is None:
                # remove all styles
                self._style_codes.clear()
            elif to:
                # replace all styles with new styles
                self._style_codes = set(to)
        elif target is None and to:
            # add new styles
            self._style_codes.update(to)
        elif target and target.issubset(self._style_codes):
            # modify specified styles
            if to is None:
                # remove target styles
                self._style_codes.difference_update(target)
            elif to:
                # replace target styles with new styles
                self._style_codes.difference_update(target)
                self._style_codes.update(to)

    def _update(
        self,
        fg: Optional[Union[Sequence[T_ColorTrans], str]] = None,
        bg: Optional[Union[Sequence[T_ColorTrans], str]] = None,
        styles: Optional[Sequence[T_StyleTrans]] = None
    ):
        r"""
        Update the :class:`ColorSeg` instance with new color and style attributes.
        """
        try:
            # foreground
            if fg is not None:
                if isinstance(fg, str):
                    self._fg_code = fg
                elif isinstance(fg, Sequence):
                    for fg_target, fg_to in fg:
                        self._update_fg(fg_target, fg_to)
            # background
            if bg is not None:
                if isinstance(bg, str):
                    self._bg_code = bg
                elif isinstance(bg, Sequence):
                    for bg_target, bg_to in bg:
                        self._update_bg(bg_target, bg_to)
            # styles
            if styles is not None:
                for style_target, style_to in styles:
                    self._update_styles(style_target, style_to)
        except Exception as e:
            raise RuntimeError("Failed To Rebuild ColorSeg Instance.") from e

    def __call__(self, text: Any, /) -> ColorSeg:
        return self.apply(text)

    def __repr__(self) -> str:
        return f"Seg(plain={repr(self.plain)},fg={repr(self.fg)},bg={repr(self.bg)},styles={repr(self.styles)}) @ [{self.istart},{self.iend})"

    def __eq__(self, other: Any) -> bool:
        return self.isequal(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __len__(self) -> int:
        return len(self.plain)

    def __deepcopy__(self, memo) -> ColorSeg:
        return self.copy()

    def __mod__(self, args: Any) -> ColorSeg:
        r"""
        Create a new :class:`ColorSeg` instance with modified attributes.

        Parameters
        ----------
            args : Tuple or Dict
                - _Tuple_: The position of elements should be: `(plain, fg, bg, styles, start)`
                - _Mapping_: The keys can be any of `"start"`, `"plain"`, `"fg"`, `"bg"`, `"styles"`, `"+fg"`, `"-fg"`, `"+bg"`, `"-bg"`, `"+styles"`, `"-styles"`.
        """
        if isinstance(args, Tuple):
            args = dict(zip(("plain", "fg", "bg", "styles", "start"), args))
        if not isinstance(args, Dict):
            raise TypeError("`args` Of ColorSeg.__mod__() Must Be A Tuple Or A Dict.")
        # start index
        seg = self.copy(istart=args.get("start"))
        # plain
        seg._update_plain(args.get("plain"), mode="=")
        seg._update_plain(args.get("+plain"), mode="+=")

        # foreground
        seg._fg_code = to_fgcode(args.get("fg")) or seg._fg_code
        # background
        seg._bg_code = to_bgcode(args.get("bg")) or seg._bg_code
        # styles
        if "styles" in args:
            seg._style_codes = to_style_codes(args["styles"])

        for key, val in args.items():
            # foreground
            if "fg" not in args and "fg" in key:
                if key == "@fg":
                    if isinstance(val, Sequence) and not isinstance(val, str) and len(val) >= 2:
                        seg._update_fg(to_fgcode(val[0]), to_fgcode(val[1]))
                    else:
                        warnings.warn(f"Invalid Value For Key '@fg' In ColorSeg.__mod__(), @fg: {val}.", RuntimeWarning)
                elif key == "-fg":
                    seg._update_fg(to_fgcode(val), "")
                elif key == "+fg":
                    seg._update_fg("", to_fgcode(val))
            # background
            if "bg" not in args and "bg" in key:
                if key == "@bg":
                    if isinstance(val, Sequence) and not isinstance(val, str) and len(val) >= 2:
                        seg._update_bg(to_bgcode(val[0]), to_bgcode(val[1]))
                    else:
                        warnings.warn(f"Invalid Value For Key '@bg' In ColorSeg.__mod__(), @bg: {val}.", RuntimeWarning)
                elif key == "-bg":
                    seg._update_bg(to_bgcode(val), "")
                elif key == "+bg":
                    seg._update_bg("", to_bgcode(val))
            # styles
            if "styles" not in args and "styles" in key:
                if key == "@styles":
                    if isinstance(val, Sequence) and not isinstance(val, str) and len(val) >= 2:
                        seg._update_styles(to_style_codes(val[0]), to_style_codes(val[1]))
                    else:
                        warnings.warn(f"Invalid Value For Key '@styles' In ColorSeg.__mod__(), @styles: {val}.", RuntimeWarning)
                elif key == "-styles":
                    seg._update_styles(to_style_codes(val), None)
                elif key == "+styles":
                    seg._update_styles(None, to_style_codes(val))
        return seg

    @property
    def istart(self) -> int:
        r"""
        Get the start index of the :class:`ColorSeg` in the original string.
        """
        return self._START_IDX

    @property
    def iend(self) -> int:
        r"""
        Get the end index of the :class:`ColorSeg` in the original string.
        """
        return self._START_IDX + len(self)

    @property
    def isfgcolored(self) -> bool:
        r"""
        Check if the :class:`ColorSeg` instance has any foreground color applied.
        """
        return bool(self.fg)

    @property
    def isbgcolored(self) -> bool:
        r"""
        Check if the :class:`ColorSeg` instance has any background color applied.
        """
        return bool(self.bg)

    @property
    def isstyled(self) -> bool:
        r"""
        Check if the :class:`ColorSeg` instance has any style applied.
        """
        return bool(self.styles)

    @property
    def isplain(self) -> bool:
        r"""
        Check if the :class:`ColorSeg` instance is plain (no color or style applied).
        """
        return not (self.isfgcolored or self.isbgcolored or self.isstyled)

    @property
    def plain(self) -> ExtStr:
        r"""
        The plain string of the :class:`ColorSeg` instance.
        """
        return self._plain

    @property
    def fg(self) -> str:
        r"""
        The foreground color code of the :class:`ColorSeg` instance.
        """
        return self._fg_code

    @property
    def bg(self) -> str:
        r"""
        The background color code of the :class:`ColorSeg` instance.
        """
        return self._bg_code

    @property
    def styles(self) -> Set[str]:
        r"""
        The set of style names applied to the :class:`ColorSeg` instance.
        """
        return self._style_codes
