"""
Type definitions for :pkg:`cobra_color` package.
"""

from typing import (Sequence, Union, Literal, Optional, Tuple, Set)


T_ColorName = Literal["d", "r", "g", "y", "b", "m", "c", "w", "ld", "lr", "lg", "ly", "lb", "lm", "lc", "lw"]
T_ColorSpec = Union[T_ColorName, int, Sequence[int]]
T_ColorTrans = Tuple[Optional[str], Optional[str]]
T_StyleName = Literal["bold", "dim", "italic", "udl", "underline", "blink", "selected", "disappear", "del", "delete"]
T_StyleModTarget = Union[Set[str], Literal["all"]]
T_StyleTrans = Tuple[Optional[T_StyleModTarget], Optional[Set[str]]]

T_ImgFillingMode = Literal["ascii", "color", "half-color", "gray", "half-gray"]
T_ImgBlockFillingMode = Literal["color", "half-color", "gray", "half-gray"]
