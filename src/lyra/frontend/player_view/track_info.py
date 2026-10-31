from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TrackInfo(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("trackInfo")
        self.title = QLabel()
        self.title.setObjectName("trackTitle")
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.artist = QLabel()
        self.artist.setObjectName("trackArtist")
        self.artist.setWordWrap(True)
        self.artist.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.album = QLabel()
        self.album.setObjectName("trackAlbum")
        self.album.setWordWrap(True)
        self.album.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title)
        layout.addWidget(self.artist)
        layout.addWidget(self.album)

    def set_track_info(self, title: str, artist: str, album: str) -> None:
        self.title.setText(title)
        self.artist.setText(artist)
        self.album.setText(album)
