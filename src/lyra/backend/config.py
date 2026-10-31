import json
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from .models import Theme


@dataclass
class Config:
    library_path: str | None = None
    theme: Theme = field(default_factory=Theme)

    def to_dict(self) -> dict:
        return {
            "library_path": self.library_path,
            "theme": self.theme.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        theme_data = data.get("theme")
        return cls(
            theme=Theme.from_dict(theme_data)
            if isinstance(theme_data, dict)
            else Theme(),
            library_path=data.get("library_path"),
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
