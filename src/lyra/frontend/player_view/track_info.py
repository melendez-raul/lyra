from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..rules import AppWidget, Elements


class TrackInfo(AppWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("trackInfo", parent)
        self.title = Elements.h1("")
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.artist = Elements.h2("")
        self.artist.setWordWrap(True)
        self.artist.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.album = Elements.h3("")
        self.album.setWordWrap(True)
        self.album.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.artist)
        self.main_layout.addWidget(self.album)

    def set_track_info(self, title: str, artist: str, album: str) -> None:
        self.title.setText(title)
        self.artist.setText(artist)
        self.album.setText(album)
