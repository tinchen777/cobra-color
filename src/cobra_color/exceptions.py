# src/cobra_color/exceptions.py
"""
Exceptions for :pkg:`cobra_color` package.
"""


# === WARNING ===
class CobraColorWarning(Warning):
    r"""Base warning class for :pkg:`cobra_color` package."""


class ParameterIgnoredWarning(CobraColorWarning):
    r"""Warning raised when a parameter is ignored."""


# === ERROR ===
class CobraColorError(Exception):
    r"""Base error class for :pkg:`cobra_color` package."""


class ImgFillingModeError(CobraColorError):
    r"""Error raised when an invalid image filling mode is specified."""


class DimensionError(CobraColorError):
    r"""Error raised when there is a dimension mismatch in image processing."""


class NotFoundError(CobraColorError):
    r"""Error raised when a requested item is not found."""
