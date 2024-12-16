import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
)

class LivePlotWindow(QDialog):
    """Secondary window to display and continuously update the plot."""
    def __init__(self, serial_number: str, rework_letter: str, base_pressure: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pressure vs Leak Valve Turns")
        self.resize(800, 600)

        self.serial_number: str = serial_number
        self.rework_letter: str = rework_letter
        self.base_pressure: str = base_pressure

        # Initialize data
        # self.pressure_up: list[float] = list()
        # self.pressure_down: list[float] = list()
        # self.turns_up: list[float] = list()
        # self.turns_down: list[float] = list()

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Set fixed axis limits and scaling
        self.ax.set_xlim(0, 12)  # x-axis from 0 to 12
        self.ax.set_ylim(1e-8, 1e-3)  # y-axis from 1e-7 to 1e-3
        self.ax.set_yscale('log')  # Logarithmic scale for y-axis

        # Add canvas to the window
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    # def add_measurement(self) -> None:
    #     """Add a new measurement and update the data lists."""
    #     if direction == 'up':
    #         self.turns_up.append(valve_position)
    #         self.pressure_up.append(pressure)
    #     else:
    #         self.turns_down.append(valve_position)
    #         self.pressure_down.append(pressure)

    def update_plot(self, valve_turns_up: list[float], pressure_up: list[float], valve_turns_down: list[float], pressure_down: list[float]) -> None:
        """Update the plot with the current data."""
        self.ax.clear()  # Clear previous data

        # Reapply fixed axes settings
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(1e-8, 1e-3)
        self.ax.set_yscale('log')

        # Plot the data
        self.ax.plot(valve_turns_up, pressure_up, marker="o", label="Pressure", color='tab:blue')
        self.ax.plot(valve_turns_down, pressure_down, marker="o", label="Pressure", color='lightskyblue')
        self.ax.set_title(f'VAT Valve #{self.serial_number}({self.rework_letter})')
        self.ax.set_xlabel("Leak Valve Turns")
        self.ax.set_ylabel("Pressure (mBar)")
        self.ax.legend()
        self.canvas.draw()  # Redraw the canvas
