# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from __future__ import annotations
from typing import (Any, Optional, Iterable, Union)

from ._color import ColorStr
from ..types import (ColorName, StyleName)


def compile_template(
    fg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    bg: Optional[Union[ColorName, int, Iterable[int]]] = None,
    styles: Optional[Iterable[StyleName]] = None
):
    r"""
    Create a template for generating `rich str` instances.

    Parameters
    ----------
        fg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The foreground color of the `rich str`.
            (Same format and rules as in :func:`ctext()`.)

        bg : Optional[Union[ColorName, int, Iterable[int]]], default to `None`
            The background color of the `rich str`.
            (Same format and rules as in :func:`ctext()`.)
        styles : Optional[Iterable[StyleName]]], default to `None`
            The styles combination of the `rich str`.
            (Same format and rules as in :func:`ctext()`.)

    Returns
    -------
        Template
            A template instance that can be used to generate :class:`ColorStr` instances.
    """
    return ColorTemplate(fg=fg, bg=bg, styles=styles)


class ColorTemplate():
    r"""
    A template class for generating `rich str` instances.
    """
    def __init__(
        self,
        fg: Any = None,
        bg: Any = None,
        styles: Any = None,
    ):
        self.__empty = ColorStr.from_str("A", fg=fg, bg=bg, styles=styles)

    def to(
        self,
        use_color: bool = True,
        use_style: bool = True
    ) -> ColorTemplate:
        r"""
        Convert the :class:`ColorTemplate` to specified color and style usage.

        Parameters
        ----------
            use_color : bool, default to `True`
                Whether to keep the color codes.

            use_style : bool, default to `True`
                Whether to keep the style codes.

        Returns
        -------
            ColorTemplate
                The :class:`ColorTemplate` instance with specified color and style usage.
        """
        self.__empty = self.__empty.to(
            use_color=use_color,
            use_style=use_style
        )

        return self

    def format(self, text: Any, /) -> ColorStr:
        r"""
        Generate a colored string using the preset template.

        Parameters
        ----------
            text : Any
                The text content to be colored.

        Returns
        -------
            ColorStr
                A :class:`ColorStr` instance.
        """
        return self.__empty.apply(text, extend="all")

    def __call__(self, text: Any, /) -> ColorStr:
        r"""
        Generate a :class:`ColorStr` instance using the preset template.
        """
        return self.format(text)
