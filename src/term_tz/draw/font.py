# -*- coding: utf-8 -*-
# Python version: 3.9
# @TianZhen

import os
from PIL import (Image, ImageDraw, ImageFont)
from typing import Tuple

from .utils import (BinaryImage, render_image)
from ..types import ImgFillingModeName


def color_font(
    text: str,
    font: str = "LLDisco",
    mode: ImgFillingModeName = "half-color",
    charset: str = "@%#*+=-:. ",
    fore_rgb: Tuple[int, int, int] = (255, 255, 255),
    back_rgb: Tuple[int, int, int] = (0, 0, 0),
    threshold: int = 5,
    size: int = 10
):
    img = Image.new("L", (100, 15), color=0)
    draw = ImageDraw.Draw(img)
    # font
    if os.path.isfile(font):
        pil_font = ImageFont.truetype(font, size=size)
    else:
        raise ValueError(f"Font '{font}' Not Supported. Please Provide A Valid TTF/OTF Font File.")

    pil_font = ImageFont.truetype(font, size=size)
    draw.text((0, 0), text, font=pil_font, fill=255)
    binary_img = BinaryImage.from_image(
        img,
        threshold=threshold,
        upper_rgb=fore_rgb,
        lower_rgb=back_rgb
    )
    return render_image(binary_img, mode=mode, charset=charset)
