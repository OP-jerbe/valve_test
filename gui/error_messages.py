from PySide6.QtWidgets import QMessageBox


def failed_to_start_message(parent, error, traceback) -> None:
    title = "Error"
    message = f"Failed to start application.\n\nError: {error}\n\n{traceback}"
    QMessageBox.critical(parent, title, message)


def failed_to_connect_to_motor(parent, error, traceback) -> None:
    title = "Error"
    message = f"Failed to connect to motor.\n\nError: {error}\n\n{traceback}"
    QMessageBox.critical(parent, title, message)


def failed_to_connect_to_pressure_gauge(parent, error, traceback) -> None:
    title = "Error"
    message = f"Failed to connect to pressure gauge.\n\nError: {error}\n\n{traceback}"
    QMessageBox.critical(parent, title, message)
