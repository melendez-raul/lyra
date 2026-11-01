from backend import Playlist
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ..rules import AppWidget
from .track_item import TrackItem


class LibraryPanel(AppWidget):
    play_requested = Signal(int)

    def __init__(self, playlist: Playlist, parent: QWidget | None = None) -> None:
        super().__init__("libraryPanel", parent)
        self._playlist = playlist
        self._items: list[TrackItem] = []
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("libraryScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.list_widget = QWidget()
        self.list_widget.setObjectName("libraryList")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()
        self.scroll_area.setWidget(self.list_widget)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)
        self.main_layout.addWidget(self.scroll_area, 1)
        self.refresh()

    def refresh(self) -> None:
        self._clear_items()
        for track in self._playlist.tracks:
            item = TrackItem(track)
            item.play_requested.connect(self.play_requested.emit)
            self._items.append(item)
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)

    def _clear_items(self) -> None:
        for item in self._items:
            self.list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()
