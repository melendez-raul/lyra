import json
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from .models import Colors, Fonts


@dataclass
class Config:
    library_path: str | None = None
    colors: Colors = field(default_factory=Colors)
    fonts: Fonts = field(default_factory=Fonts)

    def to_dict(self) -> dict:
        return {
            "library_path": self.library_path,
            "colors": self.colors.to_dict(),
            "fonts": self.fonts.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        colors = data.get("colors")
        fonts = data.get("fonts")
        return cls(
            library_path=data.get("library_path"),
            colors=Colors.from_dict(colors if isinstance(colors, dict) else {}),
            fonts=Fonts.from_dict(fonts if isinstance(fonts, dict) else {}),
        )

    @staticmethod
    def _config_path() -> Path:
        directory = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppConfigLocation
            )
        )
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "config.json"

    @classmethod
    def load(cls) -> "Config":
        path = cls._config_path()
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()
        if not isinstance(data, dict):
            return cls()
        return cls.from_dict(data)

    def save(self) -> None:
        path = self._config_path()
        path.write_text(
            json.dumps(self.to_dict(), indent=4, ensure_ascii=False), encoding="utf-8"
        )
