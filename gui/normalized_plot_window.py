import sys
import random
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
)

class NormalizedPlotWindow(QDialog):
    """Secondary window to display the final, normalized plot."""
    def __init__(self, figure: Figure, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Normalized Pressure vs Leak Valve Turns")

        self.canvas = FigureCanvas(figure)

        # Add canvas to the window
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def draw_figure(self) -> None:
        self.canvas.draw()