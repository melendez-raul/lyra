import colorsys
import re

from backend import Accent, Accents

_RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def _hue(color: str) -> float:
    match = _RGB.fullmatch(color)
    if not match:
        raise ValueError(f"Color RGB inválido: {color}")
    r, g, b = (int(v) / 255 for v in match.groups())
    return colorsys.rgb_to_hsv(r, g, b)[0]


def _gap(a: float, b: float) -> float:
    d = abs(a - b)
    return min(d, 1 - d)


def pick_accent(cover_color: str | None, accents: Accents) -> tuple[str, Accent] | None:
    if not cover_color:
        return None
    target = _hue(cover_color)
    return min(
        accents.items().items(),
        key=lambda kv: _gap(target, _hue(kv[1].primary)),
    )
