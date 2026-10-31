from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from .lyric_item import LyricItem


class LyricsPanel(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("lyricsPanel")
        self._items: list[LyricItem] = []
        self._active_index = -1
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("lyricsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.list_widget = QWidget()
        self.list_widget.setObjectName("lyricsList")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.bottom_spacer = QWidget()
        self.bottom_spacer.setFixedHeight(0)
        self.list_layout.addWidget(self.bottom_spacer)
        self.scroll_area.setWidget(self.list_widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.addWidget(self.scroll_area, 1)
        self.scroll_animation = QPropertyAnimation(
            self.scroll_area.verticalScrollBar(), b"value", self
        )
        self.scroll_animation.setDuration(400)
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_lyrics(self, lyrics: list[dict]) -> None:
        self._clear_items()
        self._active_index = -1
        for lyric in lyrics:
            item = LyricItem(time=lyric["time"], text=lyric["text"])
            self._items.append(item)
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)
        self._update_bottom_spacer()

    def set_active_lyric(self, index: int) -> None:
        if index < 0 or index >= len(self._items):
            return
        if self._active_index == index:
            return
        if self._active_index != -1:
            self._items[self._active_index].set_active(False)
        self._active_index = index
        item = self._items[index]
        item.set_active(True)
        QTimer.singleShot(0, lambda: self._scroll_to_item(item))

    def _scroll_to_item(self, item: LyricItem) -> None:
        if item not in self._items:
            return
        self.list_widget.layout().activate()  # pyright: ignore[reportOptionalMemberAccess]
        scrollbar = self.scroll_area.verticalScrollBar()
        target = item.mapTo(self.list_widget, item.rect().topLeft()).y()
        self.scroll_animation.stop()
        self.scroll_animation.setStartValue(scrollbar.value())
        self.scroll_animation.setEndValue(target)
        self.scroll_animation.start()

    def clear(self) -> None:
        self.scroll_animation.stop()
        self._clear_items()
        self._active_index = -1
        self.scroll_area.verticalScrollBar().setValue(0)
        self._update_bottom_spacer()

    def _clear_items(self) -> None:
        for item in self._items:
            self.list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()

    def _update_bottom_spacer(self) -> None: # Leaves space between the last LyricItem
        height = self.scroll_area.viewport().height()
        self.bottom_spacer.setFixedHeight(height)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_bottom_spacer()
