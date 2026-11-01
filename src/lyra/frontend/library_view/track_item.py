from pathlib import Path

from backend import Track
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..rules import AppRules, AppWidget


class TrackItem(AppWidget):
    play_requested = Signal(int)

    def __init__(self, track: Track, parent: QWidget | None = None) -> None:
        super().__init__("trackItem", parent)
        self._track = track
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.artwork = AppRules.label("")
        self.artwork.setFixedSize(75, 75)
        self.artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._set_cover(track.cover_path)
        self.title = AppRules.label(track.title)
        self.title.setWordWrap(True)
        self.artist = AppRules.description(", ".join(track.artist))
        self.artist.setWordWrap(True)
        self.album = AppRules.description(track.album)
        self.album.setWordWrap(True)
        for widget in (self.title, self.artist, self.album):
            widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.info_layout = QVBoxLayout()
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(4)
        self.info_layout.addWidget(self.title)
        self.info_layout.addWidget(self.artist)
        self.info_layout.addWidget(self.album)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(12)
        self.main_layout.addWidget(self.artwork)
        self.main_layout.addLayout(self.info_layout, 1)

    def _set_cover(self, path: str | Path | None) -> None:
        if not path:
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return
        self.artwork.setPixmap(
            pixmap.scaled(
                self.artwork.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.play_requested.emit(self._track.index)
            event.accept()
            return
        super().mousePressEvent(event)
