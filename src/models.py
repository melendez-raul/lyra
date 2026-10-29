import json
from dataclasses import dataclass


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
