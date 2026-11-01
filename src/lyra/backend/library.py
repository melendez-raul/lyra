import json
import logging
import re
import shutil
import sqlite3 as sql
from pathlib import Path

from mutagen import MutagenError
from mutagen.flac import FLAC, Picture

from .models import Metadata, Track
from .palette import COLOR_VERSION, extract_color

logger = logging.getLogger(__name__)

UNKNOWN_ARTIST = "No Artist"
UNKNOWN_ALBUM = "Unknown"

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_MAX_NAME_LENGTH = 120


class LibraryError(Exception):
    pass


class Library:
    def __init__(self, directory: Path) -> None:
        self.music_dir = directory
        self.url = self.music_dir / "library.db"
        self.supported_extensions = {".flac"}
        self._create()

    def _connect(self) -> sql.Connection:
        connection = sql.connect(self.url)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sql.Row
        return connection

    def _create(self) -> None:
        connection = None
        try:
            connection = self._connect()
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS artists (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    );
                    CREATE TABLE IF NOT EXISTS albums (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        cover_path TEXT,
                        cover_color TEXT,
                        color_version INTEGER DEFAULT 0
                    );
                    CREATE TABLE IF NOT EXISTS tracks (
                        id INTEGER PRIMARY KEY,
                        path TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        album_id INTEGER REFERENCES albums(id),
                        track_number INTEGER,
                        lyrics TEXT DEFAULT NULL
                            CHECK (lyrics IS NULL OR json_valid(lyrics))
                    );
                    CREATE TABLE IF NOT EXISTS album_artists (
                        album_id INTEGER NOT NULL REFERENCES albums(id),
                        artist_id INTEGER NOT NULL REFERENCES artists(id),
                        position INTEGER NOT NULL,
                        PRIMARY KEY (album_id, artist_id)
                    );
                    CREATE TABLE IF NOT EXISTS track_artists (
                        track_id INTEGER NOT NULL REFERENCES tracks(id),
                        artist_id INTEGER NOT NULL REFERENCES artists(id),
                        position INTEGER NOT NULL,
                        PRIMARY KEY (track_id, artist_id)
                    );
                    """
                )
        except sql.Error as error:
            raise LibraryError from error
        finally:
            if connection is not None:
                connection.close()

    def _delete(self) -> None:
        self.url.unlink()

    # ------------------------------------------------------------------
    # Lectura de metadata
    # ------------------------------------------------------------------

    @staticmethod
    def _get_tag(audio: FLAC, name: str) -> str | None:
        values = audio.get(name)
        if not values:
            return None
        value = values[0].strip()
        return value or None

    @staticmethod
    def _split_names(value: str | None) -> list[str]:
        if not value:
            return []
        names = [part.strip() for part in value.split(";")]
        return list(dict.fromkeys(name for name in names if name))

    @staticmethod
    def _parse_track_number(value: str | None) -> int | None:
        if not value:
            return None
        match = re.match(r"\s*(\d+)", value)
        return int(match.group(1)) if match else None

    def _get_metadata(self, path: Path) -> tuple[Metadata, Picture | None] | None:
        if path.suffix.lower() not in self.supported_extensions:
            return None
        audio = FLAC(path)
        if audio.get("COMMENT"):
            audio.pop("COMMENT")
            audio.save()
        picture = audio.pictures[0] if audio.pictures else None

        title = self._get_tag(audio, "TITLE") or path.stem
        album = self._get_tag(audio, "ALBUM") or UNKNOWN_ALBUM
        artist = self._split_names(self._get_tag(audio, "ARTIST"))
        album_artist = self._split_names(self._get_tag(audio, "ALBUMARTIST"))
        album_artist = album_artist or artist or [UNKNOWN_ARTIST]
        artist = artist or album_artist
        raw_lyrics = self._get_tag(audio, "LYRICS")

        metadata = Metadata(
            path=str(path),
            cover_path=None,
            title=title,
            artist=artist,
            album=album,
            album_artist=album_artist,
            track_number=self._parse_track_number(self._get_tag(audio, "TRACKNUMBER")),  # pyright: ignore[reportArgumentType]
            lyrics=self._parse_lyrics(raw_lyrics) if raw_lyrics else None,
        )
        return metadata, picture

    @staticmethod
    def _parse_lyrics(raw: str) -> str:
        lyrics = []
        pattern = re.compile(r"\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\](.*)")
        for line in raw.splitlines():
            match = pattern.match(line)
            if not match:
                continue
            minutes, seconds, fraction, text = match.groups()
            text = text.strip()
            if not text:
                continue
            timestamp = int(minutes) * 60 + int(seconds)
            if fraction:
                timestamp += int(fraction) / (10 ** len(fraction))
            lyrics.append({"time": timestamp, "text": text})
        return json.dumps(lyrics, ensure_ascii=False, indent=4)

    def _ensure_color(self, cover_path: str) -> None:
        connection = None
        try:
            connection = self._connect()
            with connection:
                row = connection.execute(
                    "SELECT id, color_version FROM albums WHERE cover_path = ?",
                    (cover_path,),
                ).fetchone()
                if row is None or row["color_version"] == COLOR_VERSION:
                    return
                connection.execute(
                    "UPDATE albums SET cover_color = ?, color_version = ? WHERE id = ?",
                    (extract_color(cover_path), COLOR_VERSION, row["id"]),
                )
        except sql.Error as error:
            raise LibraryError from error
        finally:
            if connection is not None:
                connection.close()

    # ------------------------------------------------------------------
    # Base de datos
    # ------------------------------------------------------------------

    def _get_or_create_artist(self, cursor: sql.Cursor, name: str) -> int:
        cursor.execute(
            """
            INSERT INTO artists (name)
            VALUES (?)
            ON CONFLICT (name) DO NOTHING
            """,
            (name,),
        )
        row = cursor.execute(
            "SELECT id FROM artists WHERE name = ?", (name,)
        ).fetchone()
        return row["id"]

    @staticmethod
    def _get_album_artist_ids(cursor: sql.Cursor, album_id: int) -> list[int]:
        rows = cursor.execute(
            """
            SELECT artist_id
            FROM album_artists
            WHERE album_id = ?
            ORDER BY position
            """,
            (album_id,),
        ).fetchall()
        return [row["artist_id"] for row in rows]

    def _get_or_create_album(
        self,
        cursor: sql.Cursor,
        title: str,
        cover_path: str | None,
        artist_ids: list[int],
    ) -> int:
        albums = cursor.execute(
            "SELECT id FROM albums WHERE title = ?",
            (title,),
        ).fetchall()
        for album in albums:
            album_id = album["id"]
            existing_artist_ids = self._get_album_artist_ids(cursor, album_id)
            if existing_artist_ids == artist_ids:
                return album_id
        cursor.execute(
            "INSERT INTO albums (title, cover_path) VALUES (?, ?)",
            (title, cover_path),
        )
        album_id = cursor.lastrowid
        cursor.executemany(
            """
            INSERT INTO album_artists (album_id, artist_id, position)
            VALUES (?, ?, ?)
            """,
            [
                (album_id, artist_id, position)
                for position, artist_id in enumerate(artist_ids)
            ],
        )
        return album_id  # pyright: ignore[reportReturnType]

    @staticmethod
    def _add_track_artists(
        cursor: sql.Cursor, track_id: int, artist_ids: list[int]
    ) -> None:
        cursor.executemany(
            """
            INSERT INTO track_artists (track_id, artist_id, position)
            VALUES (?, ?, ?)
            ON CONFLICT DO NOTHING
            """,
            [
                (track_id, artist_id, position)
                for position, artist_id in enumerate(artist_ids)
            ],
        )

    def insert(self, metadata: Metadata) -> None:
        connection = None
        try:
            connection = self._connect()
            with connection:
                cursor = connection.cursor()
                existing_track = cursor.execute(
                    "SELECT 1 FROM tracks WHERE path = ?",
                    (metadata.path,),
                ).fetchone()
                if existing_track:
                    return
                track_artist_ids = [
                    self._get_or_create_artist(cursor, name) for name in metadata.artist
                ]
                album_artist_ids = [
                    self._get_or_create_artist(cursor, name)
                    for name in metadata.album_artist
                ]
                album_id = self._get_or_create_album(
                    cursor, metadata.album, metadata.cover_path, album_artist_ids
                )
                cursor.execute(
                    """
                    INSERT INTO tracks (
                        path, title, album_id, track_number, lyrics
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        metadata.path,
                        metadata.title,
                        album_id,
                        metadata.track_number,
                        metadata.lyrics,
                    ),
                )
                track_id = cursor.lastrowid
                if track_id:
                    self._add_track_artists(cursor, track_id, track_artist_ids)
        except sql.Error as error:
            raise LibraryError from error
        finally:
            if connection is not None:
                connection.close()

    def get_tracks(self) -> list[Track]:
        connection = None
        try:
            connection = self._connect()
            rows = connection.execute(
                """
                SELECT
                    t.path,
                    t.title,
                    t.track_number,
                    t.lyrics,
                    al.title AS album,
                    al.cover_path,
                    al.cover_color,
                    (
                        SELECT json_group_array(name)
                        FROM (
                            SELECT ar.name
                            FROM track_artists ta
                            JOIN artists ar
                                ON ar.id = ta.artist_id
                            WHERE ta.track_id = t.id
                            ORDER BY ta.position
                        )
                    ) AS artist,
                    (
                        SELECT json_group_array(name)
                        FROM (
                            SELECT ar.name
                            FROM album_artists aa
                            JOIN artists ar
                                ON ar.id = aa.artist_id
                            WHERE aa.album_id = al.id
                            ORDER BY aa.position
                        )
                    ) AS album_artist
                FROM tracks t
                LEFT JOIN albums al ON al.id = t.album_id
                ORDER BY al.title, t.track_number, t.title
                """
            ).fetchall()
            tracks = []
            for i, row in enumerate(rows):
                data = dict(row)
                data["index"] = i
                data["artist"] = json.loads(data["artist"] or "[]")
                data["album_artist"] = json.loads(data["album_artist"] or "[]")
                tracks.append(Track.from_dict(data))
            return tracks
        except (sql.Error, ValueError, TypeError) as error:
            raise LibraryError from error
        finally:
            if connection is not None:
                connection.close()

    # ------------------------------------------------------------------
    # Organización de archivos
    # ------------------------------------------------------------------

    def process(self) -> None:
        paths = sorted(
            path
            for path in self.music_dir.rglob("*")
            if path.suffix.lower() in self.supported_extensions
        )
        for path in paths:
            try:
                self._process_file(path)
            except (OSError, ValueError, MutagenError, LibraryError) as error:
                logger.warning("Omitido %s: %s", path, error)

    def _process_file(self, path: Path) -> None:
        result = self._get_metadata(path)
        if result is None:
            return
        metadata, picture = result
        album_directory = self._create_album_dir(metadata.album_artist, metadata.album)
        metadata.path = self._move_and_rename(
            path, album_directory, metadata.title, ".flac"
        )
        if picture is not None:
            metadata.cover_path = self._save_cover(picture, album_directory)
        self.insert(metadata)
        if metadata.cover_path:
            self._ensure_color(metadata.cover_path)

    @staticmethod
    def _safe_name(name: str) -> str:
        name = _INVALID_CHARS.sub("_", name).strip()[:_MAX_NAME_LENGTH]
        name = name.strip().rstrip(". ")
        if not name:
            return "_"
        if name.split(".")[0].upper() in _RESERVED_NAMES:
            name = f"_{name}"
        return name

    def _create_album_dir(self, album_artist: list[str], album: str) -> Path:
        artist_name = ", ".join(album_artist) or UNKNOWN_ARTIST
        album_dir = (
            self.music_dir / self._safe_name(artist_name) / self._safe_name(album)
        )
        album_dir.mkdir(parents=True, exist_ok=True)
        return album_dir

    @staticmethod
    def _unique_path(directory: Path, name: str, ext: str, source: Path) -> Path:
        candidate = directory / f"{name}{ext}"
        counter = 2
        while candidate.exists() and not candidate.samefile(source):
            candidate = directory / f"{name} ({counter}){ext}"
            counter += 1
        return candidate

    @classmethod
    def _move_and_rename(cls, source: Path, to_dir: Path, name: str, ext: str) -> str:
        destination = cls._unique_path(to_dir, cls._safe_name(name), ext, source)
        if not destination.exists():
            shutil.move(source, destination)
        return str(destination)

    @staticmethod
    def _save_cover(picture: Picture, album_dir: Path) -> str:
        extension = ".png" if picture.mime == "image/png" else ".jpg"
        cover = album_dir / f"cover{extension}"
        if not cover.exists():
            cover.write_bytes(picture.data)
        return str(cover)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    music_directory = Path.home() / "Música"
    library = Library(music_directory)
    library.process()
