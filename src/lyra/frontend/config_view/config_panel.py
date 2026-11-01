from backend import Config
from backend.models import Font  # ajusta el import a donde tengas Font
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..rules import AppRules, AppWidget
from .colors_section import ColorsSection
from .fonts_section import FontsSection
from .library_path_entry import LibraryPathEntry


class ConfigPanel(AppWidget):
    config_changed = Signal()

    def __init__(self, config: Config, parent: QWidget | None = None) -> None:
        super().__init__("configPanel", parent)
        self.config = config
        self.header = QWidget()
        self.header.setObjectName("configHeader")
        self.title = AppRules.title("Configuración")
        self.save_button = AppRules.button("Save Changes")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(32, 28, 32, 0)
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.save_button)
        self.library_path = LibraryPathEntry(config.library_path)
        self.theme_section = ColorsSection(config.colors.to_dict())
        self.fonts_section = FontsSection(config.fonts.to_dict())
        self.sections = QWidget()
        self.sections.setObjectName("configSections")
        self.sections_layout = QVBoxLayout(self.sections)
        self.sections_layout.setContentsMargins(32, 28, 32, 28)
        self.sections_layout.setSpacing(28)
        self.sections_layout.addWidget(self.library_path)
        self.sections_layout.addWidget(self.theme_section)
        self.sections_layout.addWidget(self.fonts_section)
        self.sections_layout.addStretch()
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("configScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.sections)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.scroll_area, 1)
        self.library_path.path_changed.connect(self._on_library_path_changed)
        self.theme_section.transparency_changed.connect(self._on_transparency_changed)
        self.theme_section.color_changed.connect(self._on_color_changed)
        self.fonts_section.font_changed.connect(self._on_font_changed)
        self.save_button.clicked.connect(self.save_config)

    def _on_library_path_changed(self, path: str) -> None:
        self.config.library_path = path

    def _on_transparency_changed(self, value: int) -> None:
        self.config.colors.transparency = value

    def _on_color_changed(self, key: str, color: str) -> None:
        if hasattr(self.config.colors, key):
            setattr(self.config.colors, key, color)

    def _on_font_changed(self, key: str, font: dict) -> None:
        if hasattr(self.config.fonts, key):
            setattr(self.config.fonts, key, Font(**font))

    def save_config(self) -> None:
        self.config.save()
        self.config_changed.emit()
