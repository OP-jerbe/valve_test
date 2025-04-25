from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QKeyEvent
from PySide6.QtWidgets import QLineEdit, QPushButton


class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.inputs_to_check: list = []
        self.start_button: QPushButton | None = None
        self.stop_button: QPushButton | None = None

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        if arg__1.key() in (Qt.Key_Return, Qt.Key_Enter):  # type: ignore
            self.clearFocus()
        else:
            super().keyPressEvent(arg__1)

    def focusOutEvent(self, arg__1: QFocusEvent) -> None:
        super().focusOutEvent(arg__1)
        if self.start_button is not None and self.stop_button is not None:
            if all(edit.text().strip() for edit in self.inputs_to_check):
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(True)
            else:
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(False)
