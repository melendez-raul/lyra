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
    def __init__(self, app: QApplication, theme: dict[str, str]) -> None:
        self.app = app
        self.theme = theme
        self.styles_dir = resource_path("frontend/styles")
        self.assets_dir = resource_path("frontend/assets")

    def set_theme(self, theme: dict[str, str]) -> None:
        self.theme = theme
        self.apply()

    def load_qss(self, filename: str = "main.qss") -> str:
        path = self.styles_dir / filename
        qss = path.read_text(encoding="utf-8")
        import_pattern = re.compile(r'@import\s+"([^"]+)"\s*;')

        def resolve_import(match: re.Match) -> str:
            import_path = path.parent / match.group(1)
            return import_path.read_text(encoding="utf-8")

        qss = import_pattern.sub(resolve_import, qss)
        theme_tokens = {key.upper(): value for key, value in self.theme.items()}
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
