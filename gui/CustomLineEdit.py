from PySide6.QtWidgets import QLineEdit, QPushButton
from PySide6.QtGui import QFocusEvent

class CustomLineEdit(QLineEdit):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.inputs_to_check: list = []
        self.button: QPushButton | None = None
    
    def focusOutEvent(self, arg__1: QFocusEvent) -> None:
        super().focusOutEvent(arg__1)
        if self.button is not None:
            if all(edit.text().strip() for edit in self.inputs_to_check):
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)