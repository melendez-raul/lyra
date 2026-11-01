import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from ..rules import AppRules, AppWidget


class ColorsSection(AppWidget):
    transparency_changed = Signal(int)
    color_changed = Signal(str, str)

    def __init__(self, colors: dict, parent: QWidget | None = None) -> None:
        super().__init__("themeSection", parent)
        self.title = AppRules.subtitle("Colors")
        self.transparency_label = AppRules.label("Background Transparency")
        transparency = max(0, min(100, int(colors.get("transparency", 85))))
        self.transparency_slider = AppRules.slider(
            minimum=0, maximum=100, value=transparency
        )
        self.transparency_value = AppRules.label(f"{transparency}%")
        self.transparency_value.setFixedWidth(48)
        self.transparency_value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.transparency_layout = QHBoxLayout()
        self.transparency_layout.setContentsMargins(0, 0, 0, 0)
        self.transparency_layout.setSpacing(12)
        self.transparency_layout.addWidget(self.transparency_slider, 1)
        self.transparency_layout.addWidget(self.transparency_value)
        self.color_entries: dict = {}
        self.colors_layout = QVBoxLayout()
        self.colors_layout.setContentsMargins(0, 0, 0, 0)
        self.colors_layout.setSpacing(12)
        colors = {key: value for key, value in colors.items() if key != "transparency"}
        for key, color in colors.items():
            name = key.replace("_", " ").title()
            entry = self._create_color_entry(key, name, color)
            self.color_entries[key] = entry
            self.colors_layout.addWidget(entry)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(16)
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.transparency_label)
        self.main_layout.addLayout(self.transparency_layout)
        self.main_layout.addLayout(self.colors_layout)
        self.transparency_slider.valueChanged.connect(self._on_transparency_changed)

    def _on_transparency_changed(self, value: int) -> None:
        self.transparency_value.setText(f"{value}%")
        self.transparency_changed.emit(value)

    def _create_color_entry(self, key: str, name: str, color: str) -> QWidget:
        container = QWidget()
        container.setObjectName("colorEntry")
        label = AppRules.label(name)
        button = AppRules.button("")
        button.setFixedSize(30, 30)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"background-color: {color};")
        container.color = color  # pyright: ignore[reportAttributeAccessIssue]
        container.button = button  # pyright: ignore[reportAttributeAccessIssue]
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(button)
        button.clicked.connect(lambda checked=False: self._select_color(key))
        return container

    def _select_color(self, key: str) -> None:
        entry = self.color_entries[key]
        current = entry.color
        match = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", current)
        if not match:
            return
        values = tuple(map(int, match.groups()))
        dialog = QColorDialog(QColor(*values), self)
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
        if dialog.exec() != QColorDialog.DialogCode.Accepted:
            return
        color = dialog.selectedColor()
        if not color.isValid():
            return
        rgb = f"rgb({color.red()}, {color.green()}, {color.blue()})"
        self.set_color(key, rgb)
        self.color_changed.emit(key, rgb)

    def set_color(self, key: str, color: str) -> None:
        if key not in self.color_entries:
            return
        entry = self.color_entries[key]
        entry.color = color
        entry.button.setStyleSheet(f"background-color: {color};")
