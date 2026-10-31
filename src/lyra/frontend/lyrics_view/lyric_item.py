from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class LyricItem(QFrame):
    def __init__(
        self,
        time: float,
        text: str,
        is_active: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.time = time
        self.text = text
        self.is_active = False
        self.setObjectName("lyricItem")
        self.text_label = QLabel(text)
        self.text_label.setObjectName("lyricText")
        self.text_label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)
        layout.addWidget(self.text_label)
        self.set_active(is_active)

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self.setProperty("active", active)
        self.text_label.setProperty("active", active)
        self._refresh_style(self)
        self._refresh_style(self.text_label)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
