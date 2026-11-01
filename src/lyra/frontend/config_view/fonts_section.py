from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..rules import AppWidget, Elements


class FontsSection(AppWidget):
    font_changed = Signal(str, dict)  # key, {"size", "weight", "fonts"}

    def __init__(self, fonts: dict, parent: QWidget | None = None) -> None:
        super().__init__("fontsSection", parent)
        self.title = Elements.h2("Fonts")
        self.font_entries: dict = {}
        self.fonts_layout = QVBoxLayout()
        self.fonts_layout.setContentsMargins(0, 0, 0, 0)
        self.fonts_layout.setSpacing(16)
        for key, font in fonts.items():
            name = key.replace("_", " ").title()
            entry = self._create_font_entry(key, name, font)
            self.font_entries[key] = entry
            self.fonts_layout.addWidget(entry)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(16)
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.fonts_layout)

    def _create_font_entry(self, key: str, name: str, font: dict) -> QWidget:
        container = QWidget()
        container.setObjectName("fontEntry")
        container.font_data = dict(font)  # pyright: ignore[reportAttributeAccessIssue]

        size_input = Elements.input("px")
        size_input.setValidator(QIntValidator(6, 200, size_input))
        size_input.setFixedWidth(72)
        size_input.setText(str(font["size"]))

        weight_input = Elements.input("100-900")
        weight_input.setValidator(QIntValidator(100, 900, weight_input))
        weight_input.setFixedWidth(88)
        weight_input.setText(str(font["weight"]))

        fonts_input = Elements.input("Inter, Segoe UI, sans-serif")
        fonts_input.setText(", ".join(font["fonts"]))

        container.size_input = size_input  # pyright: ignore[reportAttributeAccessIssue]
        container.weight_input = weight_input  # pyright: ignore[reportAttributeAccessIssue]
        container.fonts_input = fonts_input  # pyright: ignore[reportAttributeAccessIssue]

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.addWidget(Elements.info("Size"))
        row.addWidget(size_input)
        row.addWidget(Elements.info("Weight"))
        row.addWidget(weight_input)
        row.addWidget(Elements.info("Fonts"))
        row.addWidget(fonts_input, 1)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(Elements.label(name))
        layout.addLayout(row)

        for field in (size_input, weight_input, fonts_input):
            field.editingFinished.connect(lambda k=key: self._on_edited(k))
        return container

    def _on_edited(self, key: str) -> None:
        entry = self.font_entries[key]
        old = entry.font_data
        try:
            size = int(entry.size_input.text())
        except ValueError:
            size = old["size"]
        try:
            weight = int(entry.weight_input.text())
        except ValueError:
            weight = old["weight"]
        fonts = [
            name.strip().strip("\"'") for name in entry.fonts_input.text().split(",")
        ]
        fonts = [name for name in fonts if name] or old["fonts"]
        font = {"size": size, "weight": weight, "fonts": fonts}
        self._write_fields(entry, font)
        if font == old:
            return
        entry.font_data = font
        self.font_changed.emit(key, font)

    @staticmethod
    def _write_fields(entry: QWidget, font: dict) -> None:
        entry.size_input.setText(str(font["size"]))  # pyright: ignore[reportAttributeAccessIssue]
        entry.weight_input.setText(str(font["weight"]))  # pyright: ignore[reportAttributeAccessIssue]
        entry.fonts_input.setText(", ".join(font["fonts"]))  # pyright: ignore[reportAttributeAccessIssue]

    def set_font(self, key: str, font: dict) -> None:
        if key not in self.font_entries:
            return
        entry = self.font_entries[key]
        entry.font_data = dict(font)
        self._write_fields(entry, font)
