import sys
from pathlib import Path

from backend import (
    Config,
    Controller,
    Library,
    Player,
    Playlist,
)
from frontend import MainWindow, ThemeManager
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QFileDialog


def resolve_library(config: Config) -> Path | None:
    path = Path(config.library_path) if config.library_path else None
    if path is not None and path.is_dir():
        return path
    selected = QFileDialog.getExistingDirectory(
        None, "Seleccionar biblioteca musical", str(Path.home())
    )
    if not selected:
        return None
    path = Path(selected)
    config.library_path = str(path)
    config.save()
    return path


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("Lyra")
    app.setApplicationName("Lyra")
    app.setWindowIcon(
        QIcon(str(Path(__file__).parent / "frontend/assets/Lyra-logo.png"))
    )
    config = Config.load()
    theme_manager = ThemeManager(
        app=app, colors=config.colors.to_dict(), fonts=config.fonts.to_dict()
    )
    theme_manager.apply()
    music_dir = resolve_library(config)
    if music_dir is None:
        return 0
    library = Library(music_dir)
    library.process()
    playlist = Playlist(tracks=library.get_tracks())
    player = Player()
    controller = Controller(player, playlist)
    window = MainWindow(
        controller=controller, theme_manager=theme_manager, config=config
    )
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.show()
    try:
        return app.exec()
    finally:
        player.close()


if __name__ == "__main__":
    sys.exit(main())
