from pathlib import Path

from backend import Track
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class TrackItem(QFrame):
    play_requested = Signal(int)

    def __init__(self, track: Track, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._track = track
        self.setObjectName("trackItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.artwork = QLabel()
        self.artwork.setObjectName("trackItemCover")
        self.artwork.setFixedSize(75, 75)
        self.artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._set_cover(track.cover_path)
        self.title = QLabel(track.title)
        self.title.setObjectName("trackItemTitle")
        self.title.setWordWrap(True)
        self.artist = QLabel(", ".join(track.artist))
        self.artist.setObjectName("trackItemArtist")
        self.artist.setWordWrap(True)
        self.album = QLabel(track.album)
        self.album.setObjectName("trackItemAlbum")
        self.album.setWordWrap(True)
        for widget in (self.title, self.artist, self.album):
            widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        info_layout.addWidget(self.title)
        info_layout.addWidget(self.artist)
        info_layout.addWidget(self.album)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self.artwork)
        layout.addLayout(info_layout, 1)

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
