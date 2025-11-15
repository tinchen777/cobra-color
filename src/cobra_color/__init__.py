# src/cobra_color/__init__.py
"""
cobra-color
----

A lightweight Python package for terminal display enhancements.

_Example:_

- Render a text in the terminal:

```python
from cobra_color import ctext, smart_print

c_text_1 = ctext("Hello World!", fg="r", styles=["bold"])
# Print directly from the terminal
print(c_text_1)

c_text_2 = ctext("Hello World!", fg=(255, 255, 255), styles=["udl", "bold"])
# Alternatively, you can use smart_print() to automatically support progress bar modes like tqdm and rich.
smart_print(c_text_2)

# Merge `c_text_1` and `c_text_2` while preserving their colors and style formatting.
c_text_3 = c_text_1 + c_text_2

# You can continue to use str's proprietary functions and keep the existing colors and styles.
c_text_1.upper()
```

- Render an image in the terminal:

```python
from cobra_color.draw import fmt_image, smart_print

# ASCII art
smart_print(fmt_image("example.jpg", width=80, mode="ascii"))

# Half-block color (recommended for truecolor terminals)
smart_print(fmt_image("example.jpg", width=80, mode="half-color"))
```

- Render some text with fonts in the terminal:

```python
from cobra_color.draw import fmt_font, FontName, smart_print

# Borderless grayscale font
smart_print(fmt_font("Hello World!", font=FontName.LLDISCO,, mode="half-gray", trim_border=True))
```
"""

from . import draw

from .color import ctext
from .template import compile_template
from .output import (smart_print, set_console_func)
from .format import (fmt_dict, fmt_list)


__author__ = "Zhen Tian"
__version__ = "0.2.10"

__all__ = [
    "draw",  # module
    "ctext",
    "compile_template",
    "smart_print",
    "set_console_func",
    "fmt_dict",
    "fmt_list"
]
