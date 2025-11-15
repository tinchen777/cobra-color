# tests/test_ctext.py
from cobra_color import ctext, compile_template


def test_ctext():
    for i in range(0, 256):
        a = ctext("\u2588", fg=(0, 0, i))
        assert isinstance(a, str)
        print(a, end="")
        if (i + 1) % 32 == 0:
            print()


def test_ctext_1():
    a = ctext("abcd", bg="lm", styles=["bold", "udl"])
    b = ctext("1234ff", fg="r", styles=["italic", "delete"])
    a += b
    a *= 2
    print(a.apply_to("XYZ"))
    print(a.upper())
    print(repr(a))
    print(a.iscolored())
    print(a.color_only)
    print(a.style_only)


def test_compile_template():
    template = compile_template(bg="b", styles=["bold", "udl"])
    c_str = template("Hello World!")
    assert isinstance(c_str, str)
