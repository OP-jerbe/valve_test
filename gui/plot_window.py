import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
)

class PlotWindow(QDialog):
    """Secondary window to display and continuously update the plot."""
    def __init__(self, serial_number: str, rework_letter: str, base_pressure: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pressure vs Leak Valve Turns")
        self.resize(800, 600)

        self.serial_number = serial_number
        self.rework_letter = rework_letter
        self.base_pressure = base_pressure

        # Initialize data
        self.turns = []  # Leak valve turns
        self.pressures = []  # Pressure measurements

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Set fixed axis limits and scaling
        self.ax.set_xlim(0, 12)  # x-axis from 0 to 12
        self.ax.set_ylim(1e-7, 1e-3)  # y-axis from 1e-7 to 1e-3
        self.ax.set_yscale('log')  # Logarithmic scale for y-axis

        # Add canvas to the window
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Timer for updating the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)

    def start_updating(self, interval=1000) -> None:
        """Start the timer to update the plot at a regular interval."""
        self.timer.start(interval)

    def stop_updating(self) -> None:
        """Stop the timer."""
        self.timer.stop()

    def add_measurement(self, turn, pressure) -> None:
        """Add a new measurement and update the data lists."""
        self.turns.append(turn)
        self.pressures.append(pressure)

    def update_plot(self) -> None:
        """Update the plot with the current data."""
        self.ax.clear()  # Clear previous data

        # Reapply fixed axes settings
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(1e-7, 1e-3)
        self.ax.set_yscale('log')

        # Plot the data
        self.ax.plot(self.turns, self.pressures, marker="o", label="Pressure")
        self.ax.set_title(f'VAT Valve #{self.serial_number}({self.rework_letter})')
        self.ax.set_xlabel("Leak Valve Turns")
        self.ax.set_ylabel("Pressure (mBar)")
        self.ax.legend()
        self.canvas.draw()  # Redraw the canvas





if __name__ == "__main__":
    class MainWindow(QMainWindow):
        """Main application window."""
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Main Window")
            self.resize(400, 300)

            # Button to open the plot window
            self.button = QPushButton("Start Pressure Monitoring")
            self.button.clicked.connect(self.open_plot_window)

            # Set central widget
            central_widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(self.button)
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

        def open_plot_window(self) -> None:
            """Open the plot window and simulate pressure data collection."""
            serial_number = '225'       # replace with self.gui.serial_number_input.text()
            rework_letter = 'A'         # replace with self.gui.rework_letter_input.text()
            base_pressure = '1.2e-7'    # replace with self.gui.base_pressure_input.text()
            parent = self               # replace with self.gui
            self.plot_window = PlotWindow(serial_number=serial_number, rework_letter=rework_letter, base_pressure=base_pressure, parent=parent)
            self.plot_window.start_updating()

            # Simulate adding measurements (replace with real data in practice)
            self.simulate_data_collection()
            self.plot_window.exec()

        def simulate_data_collection(self) -> None:
            """Simulate adding data to the plot (replace this with real data acquisition)."""
            def add_fake_data() -> None:
                # Generate fake leak valve turns and pressures
                turn = len(self.plot_window.turns) + 1
                pressure = random.uniform(1e-7, 1e-5)
                self.plot_window.add_measurement(turn, pressure)

            # Use a timer to simulate adding data every second
            self.data_timer = QTimer(self)
            self.data_timer.timeout.connect(add_fake_data)
            self.data_timer.start(1000)  # Add data every second

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())