from PySide6.QtCore import QObject, Signal

from .models import PlaybackStatus, Playlist, Track
from .player import Player


class Controller(QObject):
    status_changed = Signal(object)
    current_track_changed = Signal(object)
    playlist_changed = Signal(object)

    def __init__(
        self, player: Player, playlist: Playlist, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self.player = player
        self.playlist = playlist
        self.player.status_changed.connect(self._on_status_changed)
        self.player.track_finished.connect(self.next)

    @property
    def current_track(self) -> Track | None:
        return self.playlist.current

    def get_status(self) -> PlaybackStatus:
        return self.player.get_status()

    def play_index(self, index: int) -> None:
        track = self.playlist.select(index)
        if track is None:
            return
        self._play_track(track)

    def _play_track(self, track: Track) -> None:
        self.player.play(track.path)
        self.current_track_changed.emit(track)

    def play(self) -> None:
        track = self.playlist.current
        if track is None:
            if not self.playlist.tracks:
                return
            track = self.playlist.select(0)
        if track is None:
            return
        status = self.player.get_status()
        if status.state == "paused" and status.track == track.path:
            self.player.resume()
        else:
            self._play_track(track)

    def pause(self) -> None:
        self.player.pause()

    def toggle_playback(self) -> None:
        if self.player.get_status().state == "playing":
            self.pause()
        else:
            self.play()

    def next(self) -> None:
        track = self.playlist.next()
        if track is not None:
            self._play_track(track)

    def previous(self) -> None:
        status = self.player.get_status()
        if status.time > 3:
            self.player.seek(0)
            return
        track = self.playlist.previous()
        if track is not None:
            self._play_track(track)

    def seek(self, seconds: float) -> None:
        self.player.seek(seconds)

    def _on_status_changed(self, status: PlaybackStatus) -> None:
        self.status_changed.emit(status)
