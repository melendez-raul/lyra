from backend import Controller
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .library_view import LibraryPanel
from .lyrics_view import LyricsPanel
from .player_view import PlayerPanel
from .theme_manager import ThemeManager


class MainWindow(QMainWindow):
    def __init__(
        self,
        controller: Controller,
        theme_manager: ThemeManager,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.theme_manager = theme_manager
        self.setWindowTitle("Lyra")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self.player_panel = PlayerPanel()
        self.library_panel = LibraryPanel(controller.playlist)
        self.lyrics_panel = LyricsPanel()
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        self.content_stack.addWidget(self.library_panel)
        self.content_stack.addWidget(self.lyrics_panel)
        self.content_stack.setCurrentWidget(self.library_panel)
        self.view_button = QPushButton("Biblioteca")
        self.view_button.setObjectName("viewToggle")
        self.view_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_button.clicked.connect(self.toggle_view)
        self.content_container = QWidget()
        self.content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(24, 16, 24, 16)
        header_layout.setSpacing(0)
        header_layout.addWidget(self.view_button)
        header_layout.addStretch()
        content_layout.addLayout(header_layout)
        content_layout.addWidget(self.content_stack, 1)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("mainSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(self.player_panel)
        self.splitter.addWidget(self.content_container)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([320, 960])
        self.background_widget = QWidget()
        self.background_widget.setObjectName("appBackground")
        background_layout = QHBoxLayout(self.background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)
        background_layout.addWidget(self.splitter)
        self.setCentralWidget(self.background_widget)
        self._connect_controller()
        current_track = controller.current_track
        self.player_panel.set_track(current_track)
        self.player_panel.set_status(controller.get_status())
        if current_track:
            self.lyrics_panel.set_lyrics(current_track.lyrics)

    def _connect_controller(self) -> None:
        self.player_panel.previous_requested.connect(self.controller.previous)
        self.player_panel.play_pause_requested.connect(self.controller.toggle_playback)
        self.player_panel.next_requested.connect(self.controller.next)
        self.player_panel.seek_requested.connect(self.controller.seek)
        self.controller.current_track_changed.connect(self._on_track_changed)
        self.controller.status_changed.connect(self._on_status_changed)
        self.library_panel.play_requested.connect(self.controller.play_index)

    def _on_track_changed(self, track) -> None:
        self.player_panel.set_track(track)
        if track is None:
            self.lyrics_panel.set_lyrics([])
            return
        self.lyrics_panel.set_lyrics(track.lyrics)

    def toggle_view(self) -> None:
        if self.content_stack.currentWidget() == self.library_panel:
            self.show_lyrics()
        else:
            self.show_library()

    def show_library(self) -> None:
        self.content_stack.setCurrentWidget(self.library_panel)
        self.view_button.setText("Biblioteca")

    def show_lyrics(self) -> None:
        self.content_stack.setCurrentWidget(self.lyrics_panel)
        self.view_button.setText("Letras")

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

    def _on_status_changed(self, status) -> None:
        self.player_panel.set_status(status)
        self.update_lyrics_position(status.time)
