# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

from PIL import Image
import numpy as np
from typing import (Literal, Tuple, Union)

from ..color import ctext
from ..types import ImgFillingModeName


VALID_MODES = {"ascii", "color", "half-color", "gray", "half-gray"}


def render_image(
    img: Image.Image,
    mode: ImgFillingModeName = "half-color",
    charset: str = "@%#*+=-:. "
) -> str:
    r"""
    Render an image (`PIL.Image.Image`) into a string representation based on the specified mode.

    Parameters
    ----------
        img : Image.Image
            The PIL Image to be rendered.

        mode : ImgFillingModeName, default to `"half-color"`
            The rendering mode, which can be one of the following:
            - `"ascii"`: Render using ASCII characters, mapping pixel brightness to characters in `charset`.
            - `"color"`: Render using full block characters with color.
            - `"half-color"`: Render using half block characters with color, combining two pixels vertically.
            - `"gray"`: Render using full block characters in grayscale.
            - `"half-gray"`: Render using half block characters in grayscale, combining two pixels vertically.

        charset : str, default to `"@%#*+=-:. "`
            Characters used for `"ascii"` representation, ordered from darkest to lightest.

    Returns
    -------
        str
            String representation of the rendered image.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Unknown mode(ImgFillingModeName): {mode!r}. Valid Modes: {VALID_MODES}")

    if "color" not in mode:
        # Convert to grayscale
        img = img.convert("L")

    printable_str = ""
    if mode.startswith("half-"):
        # Use half block characters
        for y in range(0, img.height, 2):
            for x in range(img.width):
                upper = img.getpixel((x, y))
                lower = img.getpixel((x, y + 1)) if y + 1 < img.height else None
                if "gray" in mode:
                    fore = (upper, upper, upper)
                    back = (lower, lower, lower) if lower is not None else None
                else:
                    fore = upper
                    back = lower
                printable_str += ctext("\u2580", fg=fore, bg=back)
            printable_str += "\n"
    else:
        # Use full block characters or ASCII characters
        pixels = img.getdata()
        for i, pixel_val in enumerate(iter(pixels)):  # type: ignore
            if mode == "ascii":
                char_index = pixel_val * (len(charset) - 1) // 255
                printable_str += charset[char_index]
            elif mode == "gray":
                printable_str += ctext(
                    " ",
                    bg=(pixel_val, pixel_val, pixel_val)
                )
            elif mode == "color":
                printable_str += ctext(" ", bg=pixel_val)

            if (i + 1) % img.width == 0:
                printable_str += "\n"

    return printable_str


class BinaryImage(Image.Image):
    @classmethod
    def from_image(
        cls,
        img: Image.Image,
        threshold: int = 128,
        upper_rgb: Tuple[int, int, int] = (255, 255, 255),
        lower_rgb: Tuple[int, int, int] = (0, 0, 0)
    ):
        r"""
        Create a BinaryImage from a PIL Image.

        Parameters
        ----------
            img : Image.Image
                The source PIL Image.

            threshold : int, default to `128`
                The threshold value to binarize the image.

            upper_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
                The RGB color for pixels above the threshold.

            lower_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
                The RGB color for pixels below and equal to the threshold.
        """
        arr = np.array(img.convert("L"))
        return cls(
            arr=arr,
            threshold=threshold,
            upper_rgb=upper_rgb,
            lower_rgb=lower_rgb
        )

    def __init__(
        self,
        arr: np.ndarray,
        threshold: int = 128,
        upper_rgb: Tuple[int, int, int] = (255, 255, 255),
        lower_rgb: Tuple[int, int, int] = (0, 0, 0)
    ):
        r"""
        Initialize a BinaryImage from a numpy array.

        Parameters
        ----------
            arr : np.ndarray
                A 2D numpy array representing grayscale pixel values.

            threshold : int, default to `128`
                The threshold value to binarize the image.

            upper_rgb : Tuple[int, int, int], default to `(255, 255, 255)`
                The RGB color for pixels above the threshold.

            lower_rgb : Tuple[int, int, int], default to `(0, 0, 0)`
                The RGB color for pixels below and equal to the threshold.
        """
        self.bin_arr = (arr > threshold).astype(int)
        self.upper_rgb = upper_rgb
        self.lower_rgb = lower_rgb

    def convert(self, mode: Literal["L"] = "L", *args, **kwargs) -> Image.Image:
        if mode == "L":
            self.upper_rgb = self.rgb_to_gray(self.upper_rgb)
            self.lower_rgb = self.rgb_to_gray(self.lower_rgb)
            return self
        else:
            raise NotImplementedError(f"[BinaryImage] Conversion To Mode '{mode}' Is Not Implemented.")

    def getpixel(self, xy: Tuple[int, int]) -> Union[Tuple[int, int, int], int]:
        r"""
        Get the pixel value at the specified coordinates.

        Parameters
        ----------
            xy : Tuple[int, int]
                The (x, y) coordinates of the pixel.

        Returns
        -------
            Union[Tuple[int, int, int], int]
                The RGB value or grayscale value of the pixel.
        """
        x, y = xy
        if self.bin_arr[y, x] == 1:
            return self.upper_rgb
        else:
            return self.lower_rgb

    def getdata(self, *args, **kwargs):
        r"""
        Get the pixel data of the image.

        Returns
        -------
            Iterable[Union[Tuple[int, int, int], int, float]]
                An iterable of pixel values.
        """
        for y in range(self.bin_arr.shape[0]):
            for x in range(self.bin_arr.shape[1]):
                yield self.getpixel((x, y))

    @staticmethod
    def rgb_to_gray(rgb: Union[Tuple[int, int, int], int]) -> int:
        r"""
        Convert an RGB color to its grayscale equivalent using luminance formula.

        Parameters
        ----------
            rgb : Union[Tuple[int, int, int], int]
                The RGB color to be converted.

        Returns
        -------
            int
                The grayscale value.
        """
        if isinstance(rgb, int):
            return rgb
        else:
            if len(rgb) != 3:
                raise ValueError("RGB Tuple Must Have Exactly Three Elements.")
            if not all(0 <= val <= 255 for val in rgb):
                raise ValueError(f"RGB Values Must Be In The Range 0-255, Not {rgb}.")

            return int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])

    @property
    def width(self) -> int:
        return self.bin_arr.shape[1]

    @property
    def height(self) -> int:
        return self.bin_arr.shape[0]
