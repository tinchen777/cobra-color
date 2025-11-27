# tests/test_ctext.py

from cobra_color import (ctext, compile_template)


def test_ctext():
    for i in range(0, 256):
        a = ctext("\u2588", fg=(0, 0, i))
        assert isinstance(a, str)
        print(a, end="")
        if (i + 1) % 32 == 0:
            print()


def test_ColorStr():
    a = ctext("abcd", bg="lm", styles=["bold", "udl"])
    b = ctext("123b4ff", fg="r", styles=["italic", "delete"])
    a += b
    a *= 2
    print(a)
    print(repr(a))
    print(a.plain)
    print(a.color_only)
    print(a.style_only)
    print(a.iscombined())
    print(a.iscolored())
    print(a.pieces())
    print(a.del_pieces([1]))
    print(a.casefold())
    print(a.lower())
    print(a.swapcase())
    print(a.title())
    print(a.upper())
    print(a.center(30, ctext("-", bg="g")))
    print(a.ljust(30, "*", extend="right"))
    print(a.rjust(30, "+", extend="left"))
    print(a.zfill(30))

    print(a[:5].pieces()[-1])

    for seg in a.split("b"):
        print(seg)
    print(a.plain.split("b"))
    print(a.rsplit("b", maxsplit=1))

    print(a.replace("b", ctext("BB", fg="y")))

    print(a.strip("a"))
    print(a.rstrip("f"))
    print(a.removesuffix("4ff"))
    print(a.removeprefix("abcd1"))

    print(a.partition("fab"))
    print(a.rpartition("fab"))

    print(a.splitlines())

    print(a.to(use_color=False))


def test_compile_template():
    template = compile_template(bg="b", styles=["bold", "udl"])
    c_str = template("Hello World!")
    print(c_str)
    template.to(use_style=False)
    print(template("Hello World!"))


if __name__ == "__main__":
    test_ctext()
    test_ColorStr()
    test_compile_template()
