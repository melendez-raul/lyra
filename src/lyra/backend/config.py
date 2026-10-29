import json
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QStandardPaths


@dataclass
class Config:
    library_path: str | None = None


def _config_path() -> Path:
    directory = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        )
    )
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "config.json"


def load_config() -> Config:
    path = _config_path()
    if not path.exists():
        return Config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Config()
    if not isinstance(data, dict):
        return Config()
    library_path = data.get("library_path")
    if not isinstance(library_path, str) or not library_path.strip():
        library_path = None
    return Config(library_path=library_path)


def save_config(config: Config) -> None:
    path = _config_path()
    data = {"library_path": config.library_path}
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
