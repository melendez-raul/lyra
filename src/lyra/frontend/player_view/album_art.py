from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QSizePolicy, QWidget


class AlbumArt(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("albumArt")
        self._original_pixmap = QPixmap()
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setMinimumSize(0, 0)

    def set_cover(self, path: str | Path | None) -> None:
        pixmap = QPixmap()
        if path:
            pixmap.load(str(path))
        self._original_pixmap = pixmap
        self.updateGeometry()
        self.update()

    def clear_cover(self) -> None:
        self._original_pixmap = QPixmap()
        self.updateGeometry()
        self.update()

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        if self._original_pixmap.isNull():
            return 0
        ratio = self._original_pixmap.height() / self._original_pixmap.width()
        return round(width * ratio)

    def sizeHint(self) -> QSize:
        if self._original_pixmap.isNull():
            return QSize(300, 300)
        return QSize(400, self.heightForWidth(400))

    def paintEvent(self, event) -> None:
        if self._original_pixmap.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        target = self._original_pixmap.size()
        target.scale(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        x = (self.width() - target.width()) // 2
        y = (self.height() - target.height()) // 2
        painter.drawPixmap(
            x,
            y,
            self._original_pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ),
        )
