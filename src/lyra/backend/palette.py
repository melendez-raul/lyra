import colorsys
from pathlib import Path

from PIL import Image

COLOR_VERSION = 1


def extract_color(path: str | Path) -> str | None:
    """Color dominante real de la portada ("rgb(r, g, b)"), o None si es gris/mono."""
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            img.thumbnail((96, 96))
            quantized = img.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
    except (OSError, ValueError):
        return None

    flat = quantized.getpalette() or []
    best, best_score = None, 0.0
    for count, index in quantized.getcolors() or []:
        r, g, b = flat[index * 3 : index * 3 + 3]  # pyright: ignore[reportArgumentType, reportCallIssue, reportOperatorIssue]
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.25 or not 0.2 <= v <= 0.95:  # Descarta grises, negros y blancos
            continue
        score = count * s  # Frecuente y saturado
        if score > best_score:
            best, best_score = (r, g, b), score
    return f"rgb({best[0]}, {best[1]}, {best[2]})" if best else None
