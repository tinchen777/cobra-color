import pytest
import sys
sys.path.insert(0, "./src")

from term_tz import color_font


print(color_font(
    "Hello, Term-TZ!",
    font="/data/tianzhen/my_packages/term-tz/src/term_tz/draw/fonts/LLDISCO_.TTF",
    mode="half-gray",
    size=10
))
