from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from ..rules import AppRules, AppWidget


class LibraryPathEntry(AppWidget):
    path_changed = Signal(str)

    def __init__(
        self, library_path: str | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__("libraryPathEntry", parent)
        self.title = AppRules.subtitle("Library Path")
        self.path_input = AppRules.input(library_path or "")
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText(
            "No se ha seleccionado" if library_path == "" else library_path or ""
        )
        self.browse_button = AppRules.button("Buscar")
        self.path_layout = QHBoxLayout()
        self.path_layout.setContentsMargins(0, 0, 0, 0)
        self.path_layout.setSpacing(8)
        self.path_layout.addWidget(self.path_input, 1)
        self.path_layout.addWidget(self.browse_button)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(12)
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.path_layout)
        self.browse_button.clicked.connect(self.select_directory)

    def select_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Selecciona la biblioteca", self.path_input.text()
        )
        if not directory:
            return
        self.set_path(directory)
        self.path_changed.emit(directory)

    def set_path(self, path: str) -> None:
        self.path_input.setText(path)
