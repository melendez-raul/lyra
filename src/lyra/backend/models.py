import json
import re
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
    index: int
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
            index=data["index"],
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
    current_index: int = 0

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


@dataclass
class Theme:
    transparency: int = 85
    app_background: str = "rgb(9, 9, 15)"
    content_surface: str = "rgb(20, 20, 31)"
    player_surface: str = "rgb(16, 16, 25)"
    surface: str = "rgb(30, 30, 43)"
    surface_hover: str = "rgb(41, 41, 58)"
    border_subtle: str = "rgb(52, 52, 73)"
    title_color: str = "rgb(255, 255, 255)"
    text_primary: str = "rgb(244, 241, 250)"
    text_secondary: str = "rgb(181, 177, 197)"
    text_muted: str = "rgb(129, 125, 148)"
    text_inactive: str = "rgb(91, 88, 107)"
    accent_primary: str = "rgb(139, 92, 246)"
    accent_secondary: str = "rgb(167, 139, 250)"
    accent_tertiary: str = "rgb(109, 40, 217)"

    def to_dict(self) -> dict[str, str | int]:
        return {
            "transparency": self.transparency,
            "app_background": self.app_background,
            "content_surface": self.content_surface,
            "player_surface": self.player_surface,
            "surface": self.surface,
            "surface_hover": self.surface_hover,
            "border_subtle": self.border_subtle,
            "title_color": self.title_color,
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "text_muted": self.text_muted,
            "text_inactive": self.text_inactive,
            "accent_primary": self.accent_primary,
            "accent_secondary": self.accent_secondary,
            "accent_tertiary": self.accent_tertiary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        return cls(**data)

    def get_background(self, name: str) -> str:
        color = getattr(self, name)
        match = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color)
        if not match:
            raise ValueError(f"Color RGB inválido: {color}")
        r, g, b = map(int, match.groups())
        alpha = round(max(0, min(100, self.transparency)) * 255 / 100)
        return f"rgba({r}, {g}, {b}, {alpha})"
