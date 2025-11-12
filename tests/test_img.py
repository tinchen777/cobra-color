# tests/test_img.py
from cobra_color.draw import fmt_image


def test_fmt_image():
    result = fmt_image(
        "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
        mode="half-color",
        height=30
    )
    assert isinstance(result, str)


def test_fmt_image_ascii():
    result = fmt_image(
        "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
        mode="ascii",
        height=30
    )
    assert isinstance(result, str)
