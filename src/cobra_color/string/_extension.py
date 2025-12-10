# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Optional, Iterable, List, Any)


def to_ExtStr(obj: Any, /) -> ExtStr:
    r"""
    Convert an object to :class:`ExtStr`.
    """
    return obj if isinstance(obj, ExtStr) else ExtStr(obj)


class ExtStr(str):
    r"""
    An `extended str` class that extends the built-in :class:`str` class.
    """
    _is_fg_colored: bool = False
    _is_bg_colored: bool = False
    _is_styled: bool = False

    @classmethod
    def from_iter(cls, strings: Iterable[str], /):
        r"""
        Create an :class:`ExtStr` instance from an iterable of strings.
        """
        try:
            return cls("".join(strings))
        except TypeError as e:
            raise TypeError("All Elements In 'strings' Must Be Of Type 'str'.") from e

    def __init__(self, *args, **kwargs):
        self._is_plain = not (self.isfgcolored or self.isbgcolored or self.isstyled)

    def findall(
        self,
        sub: str,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1,
        _reverse: bool = False
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ExtStr`.
        """
        sub = to_ExtStr(sub)
        sub_len = len(sub)
        result: List[int] = []
        count = 0
        start_idx = start
        end_idx = end if end is not None else len(self)
        while maxsplit == -1 or count < maxsplit:
            if _reverse:
                idx = super().rfind(sub, start_idx, end_idx)
                end_idx = idx
            else:
                idx = super().find(sub, start_idx, end_idx)
                start_idx = idx + sub_len
            if idx == -1:
                break
            result.append(idx)
            count += 1
        if _reverse:
            result.reverse()

        return result

    def rfindall(
        self,
        sub: str,
        start: int = 0,
        end: Optional[int] = None,
        /,
        maxsplit: int = -1
    ) -> List[int]:
        r"""
        Find all occurrences of a substring in the :class:`ExtStr` in reverse order.
        """
        return self.findall(sub, start, end, maxsplit=maxsplit, _reverse=True)

    def __add__(self, other: Any, /) -> ExtStr:
        return ExtStr(super().__add__(other))

    def __mul__(self, n: Any, /) -> ExtStr:
        return ExtStr(super().__mul__(n))

    def __rmul__(self, n: Any, /):
        return self.__mul__(n)

    @property
    def isfgcolored(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any foreground color applied.
        """
        return self._is_fg_colored

    @property
    def isbgcolored(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any background color applied.
        """
        return self._is_bg_colored

    @property
    def isstyled(self) -> bool:
        r"""
        Whether the :class:`ExtStr` has any style applied.
        """
        return self._is_styled

    @property
    def isplain(self) -> bool:
        r"""
        Whether the :class:`ExtStr` is plain (no color or style applied).
        """
        return self._is_plain
