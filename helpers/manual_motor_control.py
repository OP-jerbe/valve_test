from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class MotorControl(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Create a button
        self.button = QPushButton("Move Motor", self)
        self.button.setFixedSize(200, 100)

        # Create a timer for continuous motor movement
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_motor)

        # Connect button signals
        self.button.pressed.connect(self.start_motor)
        self.button.released.connect(self.stop_motor)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def start_motor(self) -> None:
        # Start the timer when the button is pressed
        print("Motor started")
        self.timer.start(100)  # Update motor every 100ms

    def stop_motor(self) -> None:
        # Stop the timer when the button is released
        print("Motor stopped")
        self.timer.stop()

    def move_motor(self) -> None:
        # Code to move the motor goes here
        print("Motor is moving...")

if __name__ == "__main__":
    app = QApplication([])
    window = MotorControl()
    window.show()
    app.exec()