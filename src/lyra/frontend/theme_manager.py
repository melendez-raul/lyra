import re
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


class ThemeManager:
    BACKGROUND_KEYS = {  # noqa: RUF012
        "CONTENT_BG",
        "PLAYER_BG",
        "SURFACE",
        "HOVER",
    }

    def __init__(self, app: QApplication, colors: dict, fonts: dict) -> None:
        self.app = app
        self.colors = colors
        self.fonts = fonts
        self.styles_dir = resource_path("frontend/styles")
        self.assets_dir = resource_path("frontend/assets")

    def set_theme(self, colors: dict | None = None, fonts: dict | None = None) -> None:
        if colors is not None:
            self.colors = colors
        if fonts is not None:
            self.fonts = fonts
        self.reload_theme()

    @staticmethod
    def _font_family(fonts: list[str]) -> str:
        return ", ".join(f'"{name}"' if " " in name else name for name in fonts)

    def _prepare_theme(self) -> dict[str, str]:
        transparency = max(0, min(100, int(self.colors.get("transparency", 100))))
        alpha = round(transparency * 255 / 100)
        prepared: dict[str, str] = {}

        for key, value in self.colors.items():
            if key == "transparency":
                continue
            token = key.upper()
            if token in self.BACKGROUND_KEYS:
                match = re.fullmatch(
                    r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", str(value)
                )
                if not match:
                    raise ValueError(f"Color RGB inválido: {value}")
                r, g, b = map(int, match.groups())
                if any(channel > 255 for channel in (r, g, b)):
                    raise ValueError(f"Color RGB fuera de rango: {value}")
                prepared[token] = f"rgba({r}, {g}, {b}, {alpha})"
            else:
                prepared[token] = str(value)

        for key, font in self.fonts.items():
            name = key.upper()
            prepared[f"{name}_FONTS"] = self._font_family(font["fonts"])
            prepared[f"{name}_SIZE"] = f"{font['size']}px"
            prepared[f"{name}_WEIGHT"] = str(font["weight"])

        return prepared

    def load_qss(self, filename: str = "main.qss") -> str:
        path = self.styles_dir / filename
        qss = path.read_text(encoding="utf-8")
        import_pattern = re.compile(r'@import\s+"([^"]+)"\s*;')

        def resolve_import(match: re.Match) -> str:
            import_path = path.parent / match.group(1)
            return import_path.read_text(encoding="utf-8")

        qss = import_pattern.sub(resolve_import, qss)
        theme_tokens = self._prepare_theme()
        token_pattern = re.compile(
            r"@("
            + "|".join(
                re.escape(key) for key in sorted(theme_tokens, key=len, reverse=True)
            )
            + r")\b"
        )
        qss = token_pattern.sub(lambda match: theme_tokens[match.group(1)], qss)
        qss = qss.replace("@ASSETS", self.assets_dir.as_posix())
        return qss

    def reload_theme(self) -> None:
        """Relee main.qss (y sus @import) de disco, sustituye tokens y reaplica."""
        self.app.setStyleSheet(self.load_qss())

    def apply(self) -> None:
        self.reload_theme()
