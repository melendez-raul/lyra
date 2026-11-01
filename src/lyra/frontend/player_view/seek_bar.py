from backend import PlaybackStatus
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..rules import AppWidget, Elements


class ClickableSlider(QSlider):
    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(orientation, parent)
        self.setObjectName("clickableSlider")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._dragging = False

    def _update_position(self, x: float) -> None:
        ratio = x / max(1, self.width())
        ratio = max(0.0, min(1.0, ratio))
        if self.invertedAppearance():
            ratio = 1.0 - ratio
        value = self.minimum() + round(ratio * (self.maximum() - self.minimum()))
        if value != self.value():
            self.setValue(value)
            self.sliderMoved.emit(value)

    def mousePressEvent(self, event) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.orientation() == Qt.Orientation.Horizontal
        ):
            self._dragging = True
            self.setSliderDown(True)
            self.sliderPressed.emit()
            self._update_position(event.position().x())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._update_position(event.position().x())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._update_position(event.position().x())
            self._dragging = False
            self.setSliderDown(False)
            self.sliderReleased.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


def format_time(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, seconds = divmod(total, 60)
    return f"{minutes}:{seconds:02d}"


class SeekBar(AppWidget):
    seek_requested = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("seekBar", parent)
        self._duration = 0.0
        self._seeking = False
        self.current_time = Elements.label("0:00")
        self.total_time = Elements.label("--:--")
        self.slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setTracking(True)
        self.slider.sliderPressed.connect(self._start_seek)
        self.slider.sliderMoved.connect(self._preview_position)
        self.slider.sliderReleased.connect(self._finish_seek)
        self.time_layout = QHBoxLayout()
        self.time_layout.setContentsMargins(0, 0, 0, 0)
        self.time_layout.setSpacing(0)
        self.time_layout.addWidget(self.current_time)
        self.time_layout.addStretch()
        self.time_layout.addWidget(self.total_time)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.slider)
        self.main_layout.addLayout(self.time_layout)

    def set_status(self, status: PlaybackStatus) -> None:
        self._duration = status.duration or 0.0
        self.slider.setRange(0, max(0, round(self._duration * 1000)))
        self.total_time.setText(
            format_time(self._duration) if status.duration is not None else "--:--"
        )
        if not self._seeking:
            self.slider.setValue(round(status.time * 1000))
            self.current_time.setText(format_time(status.time))

    def _start_seek(self) -> None:
        self._seeking = True

    def _preview_position(self, position_ms: int) -> None:
        self.current_time.setText(format_time(position_ms / 1000))

    def _finish_seek(self) -> None:
        position = self.slider.value() / 1000
        self._seeking = False
        self.current_time.setText(format_time(position))
        self.seek_requested.emit(position)
