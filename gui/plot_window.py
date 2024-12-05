import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
)


class PlotWindow(QDialog):
    """Secondary window to display a Matplotlib plot."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matplotlib Plot")
        self.resize(800, 600)

        # Create a matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Add canvas to the window
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, plot_logic):
        """Clear the axes and use the provided logic to update the plot."""
        self.ax.clear()  # Clear the current plot
        plot_logic(self.ax)  # Call the external plotting function
        self.canvas.draw()  # Redraw the canvas


class MainWindow(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.resize(400, 300)

        # Create a button to open the plot window
        self.button = QPushButton("Open Plot Window")
        self.button.clicked.connect(self.open_plot_window)

        # Set central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_plot_window(self):
        """Open the secondary plot window and update its plot."""
        self.plot_window = PlotWindow(self)
        # Use external plotting logic to update the plot
        self.plot_window.update_plot(external_plot_logic)
        self.plot_window.exec()


def external_plot_logic(ax):
    """External function to handle plotting logic."""
    x = [0, 1, 2, 3]
    y = [0, 1, 4, 9]
    ax.plot(x, y, label="y = x^2")
    ax.set_title("External Plot Logic")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.legend()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
