# src/cobra_color/exceptions.py
"""
Exceptions for :pkg:`cobra_color` package.
"""


# === WARNING ===
class CobraColorWarning(Warning):
    """Base warning class for :pkg:`cobra_color` package."""


class ParameterIgnoredWarning(CobraColorWarning):
    """Warning raised when a parameter is ignored."""


# === ERROR ===
class CobraColorError(Exception):
    """Base error class for :pkg:`cobra_color` package."""


class ImgFillingModeError(CobraColorError):
    """Error raised when an invalid image filling mode is specified."""


class DimensionError(CobraColorError):
    """Error raised when there is a dimension mismatch in image processing."""


class NotFoundError(CobraColorError):
    """Error raised when a requested item is not found."""
