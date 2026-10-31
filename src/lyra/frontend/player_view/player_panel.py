from backend import PlaybackStatus, Track
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from .album_art import AlbumArt
from .playback_controls import PlaybackControls
from .seek_bar import SeekBar
from .track_info import TrackInfo


class PlayerPanel(QFrame):
    previous_requested = Signal()
    play_pause_requested = Signal()
    next_requested = Signal()
    seek_requested = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("playerPanel")
        self.album_art = AlbumArt()
        self.track_info = TrackInfo()
        self.seek_bar = SeekBar()
        self.controls = PlaybackControls()
        self.seek_bar.seek_requested.connect(self.seek_requested.emit)
        self.controls.previous_requested.connect(self.previous_requested.emit)
        self.controls.play_pause_requested.connect(self.play_pause_requested.emit)
        self.controls.next_requested.connect(self.next_requested.emit)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(self.album_art, 0)
        layout.addWidget(self.track_info, 0)
        layout.addStretch(1)
        layout.addWidget(self.seek_bar, 0)
        layout.addWidget(self.controls, 0)

    def set_track(self, track: Track | None) -> None:
        if track is None:
            self.album_art.clear_cover()
            self.track_info.set_track_info("", "", "")
            return
        self.album_art.set_cover(track.cover_path)
        self.track_info.set_track_info(
            title=track.title, artist=", ".join(track.artist), album=track.album
        )

    def set_status(self, status: PlaybackStatus) -> None:
        self.seek_bar.set_status(status)
        self.controls.set_playing(status.state == "playing")
        self.controls.set_enabled(status.state not in ("closed", "error"))
