from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QToolButton,
    QWidget,
)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


class PlaybackControls(QWidget):
    previous_requested = Signal()
    play_pause_requested = Signal()
    next_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("playbackControls")
        self.previous_button = QToolButton()
        self.previous_button.setObjectName("previousButton")
        self.previous_button.setIcon(QIcon(str(ASSETS_DIR / "prev.svg")))
        self.previous_button.setIconSize(QSize(22, 22))
        self.previous_button.setAccessibleName("Canción anterior")
        self.previous_button.setMouseTracking(True)
        self.previous_button.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.previous_button.clicked.connect(self.previous_requested.emit)
        self.play_button = QToolButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setIcon(QIcon(str(ASSETS_DIR / "play.svg")))
        self.play_button.setIconSize(QSize(26, 26))
        self.play_button.setAccessibleName("Reproducir")
        self.play_button.clicked.connect(self.play_pause_requested.emit)
        self.next_button = QToolButton()
        self.next_button.setObjectName("nextButton")
        self.next_button.setIcon(QIcon(str(ASSETS_DIR / "next.svg")))
        self.next_button.setIconSize(QSize(22, 22))
        self.next_button.setAccessibleName("Canción siguiente")
        self.next_button.setMouseTracking(True)
        self.next_button.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.next_button.clicked.connect(self.next_requested.emit)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addStretch()
        layout.addWidget(self.previous_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.next_button)
        layout.addStretch()

    def set_playing(self, playing: bool) -> None:
        icon_name = "pause.svg" if playing else "play.svg"
        self.play_button.setIcon(QIcon(str(ASSETS_DIR / icon_name)))
        self.play_button.setAccessibleName("Pausar" if playing else "Reproducir")

    def set_enabled(self, enabled: bool) -> None:
        self.previous_button.setEnabled(enabled)
        self.play_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
