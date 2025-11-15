# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Any, Optional, Iterable, Union)

from .color import ColorStr
from .types import (ColorName, StyleName)


def compile_template(
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
):
    r"""
    Create a template for generating colored strings with preset styles.

    Parameters
    ----------
        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            (Same format and rules as in `ctext`.)

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as in `ctext`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.
            (Same format and rules as in `ctext`.)

    Returns
    -------
        Template
            A template object that can be used to generate colored strings with the preset styles.
    """
    return ColorTemplate(fg=fg, bg=bg, styles=styles)


class ColorTemplate():
    r"""
    A template class for generating colored strings with preset styles.

    Parameters
    ----------
        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the string.
            (Same format and rules as in `ctext`.)

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the string.
            (Same format and rules as in `ctext`.)

        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the string.
            (Same format and rules as in `ctext`.)
    """
    def __init__(
        self,
        fg: Any = None,
        bg: Any = None,
        styles: Any = None,
    ):
        self.__empty = ColorStr.from_str("", fg=fg, bg=bg, styles=styles)

    def format(
        self,
        text: Any,
        use_color: bool = True,
        use_style: bool = True
    ) -> ColorStr:
        r"""
        Generate a colored string using the preset template.

        Parameters
        ----------
            text : Any
                The text content to be colored.

            use_color : bool, default to `True`
                Whether to apply color codes.

            use_style : bool, default to `True`
                Whether to apply style codes.

        Returns
        -------
            ColorStr
                The colored string with ANSI escape codes. Usage same as `str`, with `plain`, `color_only`, `style_only` properties.
        """
        return self.__empty.apply_to(text, use_color=use_color, use_style=use_style)

    def __call__(
        self,
        text: Any,
        use_color: bool = True,
        use_style: bool = True
    ) -> ColorStr:
        r"""
        Generate a colored string using the preset template.
        """
        return self.format(text, use_color=use_color, use_style=use_style)
