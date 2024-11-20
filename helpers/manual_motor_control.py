from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class ContinuousMotorControl():
    def __init__(self) -> None:
        self.timer = QTimer()
        self.timer.timeout.connect(self.move)

    def start(self) -> None:
        # Start the timer when the button is pressed
        print("Motor started")
        self.timer.start(100)  # Update motor every 100ms

    def stop(self) -> None:
        # Stop the timer when the button is released
        print("Motor stopped")
        self.timer.stop()

    def move(self) -> None:
        # Code to move the motor goes here
        print("Motor is moving...")




class MotorControlWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create buttons for clockwise and counter-clockwise movement
        self.open_button = QPushButton("Open (Counter-Clockwise)", self)
        self.close_button = QPushButton("Close (Clockwise)", self)

        # Set button sizes
        self.open_button.setFixedSize(200, 100)
        self.close_button.setFixedSize(200, 100)

        # Create a timer for continuous motor movement
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_motor)

        # Variable to store the current motor direction
        self.direction = None  # 'clockwise' or 'counterclockwise'

        # Connect button signals
        self.open_button.pressed.connect(self.start_counterclockwise_motor)
        self.open_button.released.connect(self.stop_motor)

        self.close_button.pressed.connect(self.start_clockwise_motor)
        self.close_button.released.connect(self.stop_motor)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.open_button)
        layout.addWidget(self.close_button)
        self.setLayout(layout)

    def start_clockwise_motor(self):
        # Set direction to clockwise and start the motor
        self.direction = 'clockwise'
        print("Motor moving clockwise")
        self.timer.start(100)  # Update motor every 100ms

    def start_counterclockwise_motor(self):
        # Set direction to counterclockwise and start the motor
        self.direction = 'counterclockwise'
        print("Motor moving counterclockwise")
        self.timer.start(100)  # Update motor every 100ms

    def stop_motor(self):
        # Stop the motor when the button is released
        print("Motor stopped")
        self.timer.stop()
        self.direction = None

    def move_motor(self):
        # Code to move the motor based on the current direction
        if self.direction == 'clockwise':
            print("Motor is moving clockwise...")
            # Insert motor control code to rotate clockwise here
        elif self.direction == 'counterclockwise':
            print("Motor is moving counterclockwise...")
            # Insert motor control code to rotate counterclockwise here
        else:
            print("No direction set")

if __name__ == "__main__":
    app = QApplication([])
    window = MotorControlWindow()
    window.show()
    app.exec()
