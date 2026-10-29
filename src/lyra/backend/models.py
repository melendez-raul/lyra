import json
from dataclasses import dataclass
from typing import Literal


@dataclass
class Metadata:
    path: str
    cover_path: str | None
    title: str
    artist: list[str]
    album: str
    album_artist: list[str]
    track_number: int
    lyrics: str | None


@dataclass
class Track:
    path: str
    title: str
    artist: list[str]
    album: str
    album_artist: list[str]
    cover_path: str | None
    track_number: int
    lyrics: list[dict]

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        lyrics = data.get("lyrics")
        if isinstance(lyrics, str):
            lyrics = json.loads(lyrics) if lyrics else []
        return cls(
            path=data["path"],
            title=data["title"],
            artist=data["artist"],
            album=data["album"],
            album_artist=data["album_artist"],
            cover_path=data["cover_path"],
            track_number=data["track_number"],
            lyrics=lyrics or [],
        )


PlaybackState = Literal["loading", "playing", "paused", "stopped", "error", "closed"]


@dataclass(frozen=True, slots=True)
class PlaybackStatus:
    state: PlaybackState
    track: str | None
    time: float
    duration: float | None


@dataclass
class Playlist:
    tracks: list[Track]
    current_index: int = -1

    @property
    def current(self) -> Track | None:
        if not 0 <= self.current_index < len(self.tracks):
            return None
        return self.tracks[self.current_index]

    def select(self, index: int) -> Track | None:
        if not 0 <= index < len(self.tracks):
            return None
        self.current_index = index
        return self.current

    def next(self) -> Track | None:
        if self.current_index + 1 >= len(self.tracks):
            return None
        self.current_index += 1
        return self.current

    def previous(self) -> Track | None:
        if self.current_index <= 0:
            return None
        self.current_index -= 1
        return self.current
