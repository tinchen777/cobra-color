.. raw:: html

    <div align="center">
        <h2 id="title">🐱‍👤 cobra-color 🐱‍👤</h2>
    </div>

.. image:: https://img.shields.io/pypi/v/cobra-color.svg
    :target: https://pypi.org/project/cobra-color/
.. image:: https://img.shields.io/pypi/pyversions/cobra-color.svg
.. image:: https://github.com/tinchen777/cobra-color/actions/workflows/test.yml/badge.svg
    :target: https://github.com/tinchen777/cobra-color/actions/workflows/test.yml
.. image:: https://codecov.io/gh/tinchen777/cobra-color/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/tinchen777/cobra-color
.. image:: https://img.shields.io/github/license/tinchen777/cobra-color.svg

.. image:: https://img.shields.io/badge/pull%20requests-welcome-brightgreen.svg
    :target: https://github.com/tinchen777/cobra-color/pulls
.. image:: https://img.shields.io/github/stars/tinchen777/cobra-color.svg


About
=====

A lightweight Python library for enhanced terminal display: simple text color/style conventions and image-to-terminal rendering.

- Python: 3.9+
- Runtime deps: Pillow (>=9,<11), NumPy (>=1.21,<2)


Features
========

- 🚀 Concise color/style names for terminal text.
- 🚀 Image rendering in multiple modes: ASCII, color, half-color, gray, half-gray.
- 🚀 Minimal dependencies and easy integration.


Installation
============

Stable (once published):

.. code-block:: bash

    pip install cobra-color


Quick Start
===========

- Render a text in the terminal:

  .. code-block:: python

      from cobra_color import ctext, smart_print

      c_text_1 = ctext("Hello World!", fg="r", styles=["bold"])
      print(c_text_1)

      c_text_2 = ctext("Hello World!", fg=(255, 255, 255), styles=["udl", "bold"])
      smart_print(c_text_2)

      c_text_3 = c_text_1 + c_text_2

      c_text_1.upper()

- Render an image in the terminal:

  .. code-block:: python

      from cobra_color.draw import fmt_image, smart_print

      # ASCII art
      smart_print(fmt_image("example.jpg", width=80, mode="ascii"))

      # Half-block color
      smart_print(fmt_image("example.jpg", width=80, mode="half-color"))

- Render some text with fonts in the terminal:

  .. code-block:: python

      from cobra_color.draw import fmt_font, FontName, smart_print

      smart_print(fmt_font("Hello World!", font=FontName.LLDISCO, mode="half-gray", trim_border=True))


Image Modes
===========

- ``ascii``: monochrome ASCII using a density charset.
- ``color``: colorized character fill.
- ``half-color``: half-block characters with color.
- ``gray``: grayscale characters.
- ``half-gray``: half-block grayscale.

Tip: For best results, use a TrueColor-capable terminal and a monospaced font.


Requirements
===========

- Python >= 3.9
- ``Pillow`` >= 9.0, < 11
- ``NumPy`` >= 1.21, < 2.0


License
=======

See LICENSE in the repository.


Links
=====

- Homepage/Repo: https://github.com/tinchen777/cobra-color.git
- Issues: https://github.com/tinchen777/cobra-color.git/issues
