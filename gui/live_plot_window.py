import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QVBoxLayout, QDialog

class LivePlotWindow(QDialog):
    """Secondary window to display and continuously update the plot."""
    def __init__(self, serial_number: str, rework_letter: str, base_pressure: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pressure vs Leak Valve Turns")

        self.serial_number: str = serial_number
        self.rework_letter: str = rework_letter
        self.base_pressure: str = base_pressure

        # Create matplotlib figure and canvas
        self.fig = plt.figure(dpi=200, frameon=True, edgecolor='k', linewidth=2, figsize=(11*0.6,8*0.5))
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_title(f'VAT Valve #{self.serial_number}({self.rework_letter})')
        self.ax.set_xlabel("Leak Valve Turns")
        self.ax.set_ylabel("Pressure (mBar)")
        self.ax.grid()
        self.canvas = FigureCanvas(self.fig)

        # Set fixed axis limits and scaling
        self.ax.set_xlim(-0.5, 12.5)
        self.ax.set_ylim(1e-8, 1e-3)
        self.ax.tick_params(axis='both', labelsize=8)
        self.ax.set_yscale('log')

        # Add canvas to the window
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.show()

    def update_plot(self, valve_turns_up: list[float], pressure_up: list[float], valve_turns_down: list[float], pressure_down: list[float]) -> None:
        """Update the plot with the current data."""
        self.ax.clear()  # Clear previous data

        # Reapply fixed axes settings
        self.ax.set_xlim(-0.5, 12.5)
        self.ax.set_ylim(1e-8, 1e-3)
        self.ax.tick_params(axis='both', labelsize=8)
        self.ax.set_yscale('log')

        # Plot the data
        self.ax.plot(valve_turns_up, pressure_up, marker="o", markersize=2, label="Opening", color='tab:blue')
        self.ax.plot(valve_turns_down, pressure_down, marker="o", markersize=2, label="Closing", color='lightskyblue')
        self.ax.grid()
        self.ax.set_title(f'VAT Valve #{self.serial_number}({self.rework_letter})')
        self.ax.set_xlabel("Leak Valve Turns")
        self.ax.set_ylabel("Pressure (mBar)")
        self.ax.legend(fontsize=5)
        self.canvas.draw()
