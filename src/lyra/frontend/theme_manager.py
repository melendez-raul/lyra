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
        "APP_BACKGROUND",
        "CONTENT_SURFACE",
        "PLAYER_SURFACE",
        "SURFACE",
        "SURFACE_HOVER",
    }

    def __init__(self, app: QApplication, theme: dict) -> None:
        self.app = app
        self.theme = theme
        self.styles_dir = resource_path("frontend/styles")
        self.assets_dir = resource_path("frontend/assets")

    def set_theme(self, theme: dict[str, str | int]) -> None:
        self.theme = theme
        self.apply()

    def _prepare_theme(self) -> dict[str, str]:
        transparency = max(0, min(100, int(self.theme.get("transparency", 100))))
        alpha = round(transparency * 255 / 100)
        prepared = {}
        for key, value in self.theme.items():
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
            elif key != "transparency":
                prepared[token] = str(value)
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

    def apply(self) -> None:
        stylesheet = self.load_qss()
        self.app.setStyleSheet(stylesheet)
