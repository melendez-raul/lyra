import json
import re
import sqlite3 as sql
from pathlib import Path

from mutagen.flac import FLAC

from .models import Metadata, Track


class LibraryError(Exception):
    pass


class Library:
    def __init__(self, directory: Path) -> None:
        self.music_dir = directory
        self.url = self.music_dir / "library.db"
        self.metadata_tags = [
            "TITLE",
            "ARTIST",
            "ALBUM",
            "ALBUMARTIST",
            "TRACKNUMBER",
            "LYRICS",
        ]
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
                        cover_path TEXT
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

    def _get_metadata(self, path: Path) -> Metadata | None:
        if path.suffix.lower() not in self.supported_extensions:
            return None
        audio = FLAC(path)
        cover_path = None
        if audio.get("COMMENT"):
            audio.pop("COMMENT")
            audio.save()
        if audio.pictures:
            image = audio.pictures[0]
            cover_path = path.with_suffix(".jpg")
            cover_path.write_bytes(image.data)
        metadata = {}
        for tag_name in self.metadata_tags:
            tag = audio.get(tag_name)
            if not tag:
                metadata[tag_name] = None
                continue
            value = tag[0]
            if tag_name in ("ARTIST", "ALBUMARTIST"):
                metadata[tag_name] = [artist.strip() for artist in value.split(";")]
            elif tag_name == "TRACKNUMBER":
                metadata[tag_name] = int(value.split("/")[0].strip())
            elif tag_name == "LYRICS":
                metadata[tag_name] = self._parse_lyrics(value)
            else:
                metadata[tag_name] = value.strip()
        return Metadata(
            path=str(path),
            cover_path=str(cover_path) if cover_path else None,
            title=metadata["TITLE"],
            artist=metadata["ARTIST"] or [],
            album=metadata["ALBUM"],
            album_artist=metadata["ALBUMARTIST"] or [],
            track_number=metadata["TRACKNUMBER"],
            lyrics=metadata["LYRICS"],
        )

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

    def process(self) -> None:
        paths = [
            path
            for path in self.music_dir.rglob("*")
            if path.suffix.lower() in self.supported_extensions
        ]
        for path in paths:
            metadata = self._get_metadata(path)
            if metadata is None:
                continue
            album_directory = self._create_album_dir(
                metadata.album_artist, metadata.album
            )
            metadata.path = self._move_and_rename(
                metadata.path, album_directory, metadata.title, ".flac"
            )
            if metadata.cover_path is not None:
                metadata.cover_path = self._move_and_rename(
                    metadata.cover_path, album_directory, "cover", ".jpg"
                )
            self.insert(metadata)

    def _create_album_dir(self, album_artist: list[str], album: str) -> Path:
        album_artists = ", ".join(album_artist)
        album_artist_dir = self.music_dir / album_artists
        album_artist_dir.mkdir(parents=True, exist_ok=True)
        album_dir = album_artist_dir / album
        album_dir.mkdir(parents=True, exist_ok=True)
        return album_dir

    @staticmethod
    def _move_and_rename(path: str, to_dir: Path, name: str, ext: str) -> str:
        new_path = Path(path).rename((to_dir / name).with_suffix(ext))
        return str(new_path)


if __name__ == "__main__":
    music_directory = Path.home() / "Música"
    library = Library(music_directory)
    library.process()
