from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QToolButton,
    QWidget,
)


class Elements:
    @staticmethod
    def h1(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("h1")
        return widget

    @staticmethod
    def h2(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("h2")
        return widget

    @staticmethod
    def h3(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("h3")
        return widget

    @staticmethod
    def label(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("label")
        return widget

    @staticmethod
    def info(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("info")
        return widget

    @staticmethod
    def inactive(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("inactive")
        return widget

    @staticmethod
    def lyric(text: str) -> QLabel:
        widget = QLabel(text)
        widget.setObjectName("lyric")
        return widget

    @staticmethod
    def button(text: str) -> QPushButton:
        widget = QPushButton(text)
        widget.setObjectName("button")
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        return widget

    @staticmethod
    def icon_button(
        icon: QIcon | str | Path,
        tooltip: str = "",
        icon_size: int = 22,
        object_name: str = "iconButton",
    ) -> QToolButton:
        widget = QToolButton()
        widget.setObjectName(object_name)
        widget.setProperty("appRole", "iconButton")
        if isinstance(icon, QIcon):
            widget.setIcon(icon)
        else:
            widget.setIcon(QIcon(str(icon)))
        widget.setIconSize(QSize(icon_size, icon_size))
        widget.setToolTip(tooltip)
        widget.setAccessibleName(tooltip)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        widget.setMouseTracking(True)
        widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        return widget

    @staticmethod
    def toggle_button(
        text: str, object_name: str = "toggleButton", checked: bool = False
    ) -> QPushButton:
        widget = QPushButton(text)
        widget.setObjectName(object_name)
        widget.setCheckable(True)
        widget.setChecked(checked)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        return widget

    @staticmethod
    def input(placeholder: str = "") -> QLineEdit:
        widget = QLineEdit()
        widget.setObjectName("input")
        widget.setPlaceholderText(placeholder)
        return widget

    @staticmethod
    def slider(
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        minimum: int = 0,
        maximum: int = 100,
        value: int = 0,
    ) -> QSlider:
        widget = QSlider(orientation)
        widget.setObjectName("appSlider")
        widget.setRange(minimum, maximum)
        widget.setValue(value)
        return widget

    @staticmethod
    def card() -> QFrame:
        widget = QFrame()
        widget.setObjectName("card")
        return widget


class AppWidget(QWidget):
    def __init__(self, object_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


@dataclass
class Standards:
    l1_spacing = ()
    l2_spacing = ()
    l3_spacing = ()
