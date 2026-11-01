from pathlib import Path

from backend import Config, Controller
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .accents import pick_accent
from .config_view import ConfigPanel
from .library_view import LibraryPanel
from .lyrics_view import LyricsPanel
from .player_view import PlayerPanel
from .rules import Elements
from .theme_manager import ThemeManager

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "icons"


class MainWindow(QMainWindow):
    def __init__(
        self,
        controller: Controller,
        theme_manager: ThemeManager,
        config: Config,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.controller = controller
        self.theme_manager = theme_manager
        self.config = config
        self._library_path = config.library_path
        self._accent_name: str | None = None

        # ==================================
        # WINDOW CONFIGURATION
        # ==================================

        self.setWindowTitle("Lyra")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        # ==================================
        # COMPONENTS
        # ==================================

        self.player_panel = PlayerPanel()

        self.library_panel = LibraryPanel(self.controller.playlist)

        self.lyrics_panel = LyricsPanel()

        self.config_panel = ConfigPanel(self.config)

        # ==================================
        # CONTENT STACK
        # ==================================

        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")

        self.content_stack.addWidget(self.library_panel)
        self.content_stack.addWidget(self.lyrics_panel)
        self.content_stack.addWidget(self.config_panel)

        self.content_stack.setCurrentWidget(self.library_panel)

        # ==================================
        # NAVIGATION BUTTONS
        # ==================================

        self.view_button = Elements.button("Biblioteca")
        self.view_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.config_button = Elements.icon_button(
            icon=ASSETS_DIR / "config.svg",
            tooltip="Configuración",
            icon_size=22,
        )
        self.config_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # ==================================
        # CONTENT HEADER
        # ==================================

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(24, 16, 24, 16)
        self.header_layout.setSpacing(0)

        self.header_layout.addWidget(self.view_button)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.config_button)

        # ==================================
        # CONTENT CONTAINER
        # ==================================

        self.content_container = QWidget()
        self.content_container.setObjectName("contentContainer")

        self.content_layout = QVBoxLayout(self.content_container)

        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.content_layout.addLayout(self.header_layout)

        self.content_layout.addWidget(self.content_stack, 1)

        # ==================================
        # MAIN SPLITTER
        # ==================================

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.splitter.setObjectName("mainSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(0)

        self.splitter.addWidget(self.player_panel)
        self.splitter.addWidget(self.content_container)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([320, 960])

        # ==================================
        # BACKGROUND
        # ==================================

        self.background_widget = QWidget()
        self.background_widget.setObjectName("appBackground")

        self.background_layout = QHBoxLayout(self.background_widget)

        self.background_layout.setContentsMargins(0, 0, 0, 0)
        self.background_layout.setSpacing(0)

        self.background_layout.addWidget(self.splitter)

        self.setCentralWidget(self.background_widget)

        # ==================================
        # SIGNALS
        # ==================================

        self._connect_controller()
        self._connect_navigation()

        # ==================================
        # INITIAL STATE
        # ==================================

        self._initialize_player()

    # ==================================
    # CONNECTIONS
    # ==================================

    def _connect_controller(self) -> None:

        self.player_panel.previous_requested.connect(self.controller.previous)

        self.player_panel.play_pause_requested.connect(self.controller.toggle_playback)

        self.player_panel.next_requested.connect(self.controller.next)

        self.player_panel.seek_requested.connect(self.controller.seek)

        self.controller.current_track_changed.connect(self._on_track_changed)

        self.controller.status_changed.connect(self._on_status_changed)

        self.library_panel.play_requested.connect(self.controller.play_index)

        self.controller.playlist_changed.connect(self.library_panel.set_playlist)
        self.config_panel.config_changed.connect(self._on_config_changed)

    def _connect_navigation(self) -> None:

        self.view_button.clicked.connect(self.toggle_view)

        self.config_button.clicked.connect(self.show_config)

    # ==================================
    # INITIALIZATION
    # ==================================

    def _initialize_player(self) -> None:

        current_track = self.controller.current_track

        self.player_panel.set_track(current_track)

        self.player_panel.set_status(self.controller.get_status())

        if current_track:
            self.lyrics_panel.set_lyrics(current_track.lyrics)

    # ==================================
    # NAVIGATION
    # ==================================

    def toggle_view(self) -> None:

        current = self.content_stack.currentWidget()

        if current == self.library_panel:
            self.show_lyrics()
        else:
            self.show_library()

    def show_library(self) -> None:

        self.content_stack.setCurrentWidget(self.library_panel)

        self.view_button.setText("Biblioteca")

    def show_lyrics(self) -> None:

        self.content_stack.setCurrentWidget(self.lyrics_panel)

        self.view_button.setText("Letras")

    def show_config(self) -> None:

        self.content_stack.setCurrentWidget(self.config_panel)

    # ==================================
    # TRACK UPDATES
    # ==================================

    def _on_track_changed(self, track) -> None:
        self._apply_cover_theme(track)
        self.player_panel.set_track(track)

        if track is None:
            self.lyrics_panel.set_lyrics([])
            return

        self.lyrics_panel.set_lyrics(track.lyrics)

    # ==================================
    # LYRICS SYNCHRONIZATION
    # ==================================

    def update_lyrics_position(self, position: float) -> None:

        track = self.controller.current_track

        if not track or not track.lyrics:
            return

        active_index = -1

        for index, lyric in enumerate(track.lyrics):
            if lyric["time"] <= position:
                active_index = index
            else:
                break

        if active_index != -1:
            self.lyrics_panel.set_active_lyric(active_index)

    # ==================================
    # PLAYBACK STATUS
    # ==================================

    def _on_status_changed(self, status) -> None:

        self.player_panel.set_status(status)

        self.update_lyrics_position(status.time)

    def _on_config_changed(self) -> None:
        self._accent_name = "__force__"
        self._apply_cover_theme(self.controller.current_track)
        if self.config.library_path != self._library_path:
            self._library_path = self.config.library_path
            self.controller.load_library(self.config.library_path)  # pyright: ignore[reportArgumentType]
            self._initialize_player()

    def _apply_cover_theme(self, track) -> None:
        pick = None
        if track and self.config.dynamic_colors:
            pick = pick_accent(track.cover_color, self.config.accents)
        name = pick[0] if pick else None
        if name == self._accent_name:
            return
        self._accent_name = name
        colors = self.config.colors.to_dict()
        if pick:
            colors.update(pick[1].to_dict())
        self.theme_manager.set_theme(colors, self.config.fonts.to_dict())
