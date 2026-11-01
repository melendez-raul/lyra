import colorsys
import json
import re
from dataclasses import asdict, dataclass, field, fields
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
    cover_color: str | None = None

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
            cover_color=data["cover_color"],
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


FONT_FAMILY = ["Inter", "Segoe UI", "Noto Sans", "sans-serif"]


@dataclass
class Font:
    size: int
    weight: int = 400
    fonts: list[str] = field(default_factory=lambda: list(FONT_FAMILY))


@dataclass
class Colors:
    transparency: int = 80
    player_bg: str = "rgb(16, 16, 25)"
    content_bg: str = "rgb(20, 20, 31)"
    surface: str = "rgb(30, 30, 43)"
    hover: str = "rgb(41, 41, 58)"
    text: str = "rgb(244, 241, 250)"
    info: str = "rgb(181, 177, 197)"
    inactive: str = "rgb(91, 88, 107)"
    primary: str = "rgb(139, 92, 246)"
    secondary: str = "rgb(167, 139, 250)"
    tertiary: str = "rgb(109, 40, 217)"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Colors":
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in names})


@dataclass
class Fonts:
    h1: Font = field(default_factory=lambda: Font(40, 700))
    h2: Font = field(default_factory=lambda: Font(30, 700))
    h3: Font = field(default_factory=lambda: Font(20, 700))
    label: Font = field(default_factory=lambda: Font(14, 500))
    info: Font = field(default_factory=lambda: Font(14, 500))
    inactive: Font = field(default_factory=lambda: Font(14))
    lyric: Font = field(default_factory=lambda: Font(30, 500))
    lyric_active: Font = field(default_factory=lambda: Font(50, 800))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Fonts":
        default = cls()
        kwargs = {}
        for f in fields(cls):
            if isinstance(data.get(f.name), dict):
                base = asdict(getattr(default, f.name))
                kwargs[f.name] = Font(**{**base, **data[f.name]})
        return cls(**kwargs)


_RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")


def _shade(primary: str, delta: float) -> str:
    match = _RGB.fullmatch(primary)
    if not match:
        raise ValueError(f"Color RGB inválido: {primary}")
    r, g, b = (int(v) / 255 for v in match.groups())
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.05, min(0.95, l + delta))
    return "rgb({}, {}, {})".format(
        *(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s))
    )


@dataclass
class Accent:
    primary: str
    secondary: str = ""
    tertiary: str = ""

    def __post_init__(self) -> None:
        if not self.secondary:
            self.secondary = _shade(self.primary, +0.10)
        if not self.tertiary:
            self.tertiary = _shade(self.primary, -0.15)

    def set_primary(self, primary: str) -> None:
        self.primary = primary
        self.secondary = _shade(primary, +0.10)
        self.tertiary = _shade(primary, -0.15)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Accent":
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in names})


@dataclass
class Accents:
    pink: Accent = field(default_factory=lambda: Accent("rgb(236, 72, 153)"))
    red: Accent = field(default_factory=lambda: Accent("rgb(239, 68, 68)"))
    orange: Accent = field(default_factory=lambda: Accent("rgb(249, 115, 22)"))
    yellow: Accent = field(default_factory=lambda: Accent("rgb(234, 179, 8)"))
    green: Accent = field(default_factory=lambda: Accent("rgb(34, 197, 94)"))
    teal: Accent = field(default_factory=lambda: Accent("rgb(20, 184, 166)"))
    blue: Accent = field(default_factory=lambda: Accent("rgb(59, 130, 246)"))
    violet: Accent = field(default_factory=lambda: Accent("rgb(139, 92, 246)"))

    def items(self) -> dict[str, Accent]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Accents":
        kwargs = {}
        for f in fields(cls):
            value = data.get(f.name)
            if isinstance(value, dict) and "primary" in value:
                kwargs[f.name] = Accent.from_dict(value)
        return cls(**kwargs)
