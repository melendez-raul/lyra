from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout

from ..rules import AppWidget, Elements

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


class PlaybackControls(AppWidget):
    previous_requested = Signal()
    play_pause_requested = Signal()
    next_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__("playbackControls", parent)
        self.previous_button = Elements.icon_button(
            ASSETS_DIR / "prev.svg",
            tooltip="Anterior",
            icon_size=22,
            object_name="previousButton",
        )
        self.play_button = Elements.icon_button(
            ASSETS_DIR / "play.svg",
            tooltip="Reproducir",
            icon_size=50,
            object_name="playButton",
        )
        self.next_button = Elements.icon_button(
            ASSETS_DIR / "next.svg",
            tooltip="Siguiente",
            icon_size=22,
            object_name="nextButton",
        )
        self.previous_button.clicked.connect(self.previous_requested.emit)
        self.play_button.clicked.connect(self.play_pause_requested.emit)
        self.next_button.clicked.connect(self.next_requested.emit)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(8)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.previous_button)
        self.main_layout.addWidget(self.play_button)
        self.main_layout.addWidget(self.next_button)
        self.main_layout.addStretch()

    def set_playing(self, playing: bool) -> None:
        icon_name = "pause.svg" if playing else "play.svg"
        self.play_button.setIcon(QIcon(str(ASSETS_DIR / icon_name)))
        self.play_button.setAccessibleName("Pausar" if playing else "Reproducir")
        self.play_button.setToolTip("Pausar" if playing else "Reproducir")

    def set_enabled(self, enabled: bool) -> None:
        self.previous_button.setEnabled(enabled)
        self.play_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
