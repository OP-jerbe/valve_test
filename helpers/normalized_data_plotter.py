try:
    from helpers.constants import AOI_LOWER_BOUND, AOI_UPPER_BOUND
except Exception:
    from constants import AOI_LOWER_BOUND, AOI_UPPER_BOUND
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure


class NormalizedPlot:
    def __init__(
        self, valve_serial_number: str, rework_letter: str, base_pressure: str
    ) -> None:
        self.serial_number: str = valve_serial_number
        self.rework_letter: str = rework_letter
        self.base_pressure: float = float(base_pressure)

        self.fig = plt.figure(
            dpi=200,
            frameon=True,
            edgecolor="k",
            linewidth=2,
            figsize=(11 * 0.6, 8 * 0.5),
        )
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_title(
            f"VAT Valve: {self.serial_number}({self.rework_letter})", fontsize=10
        )
        self.ax.set_xlabel("Valve Turns", fontsize=7)
        self.ax.set_ylabel("Normalized Pressure (mBar)", fontsize=7)
        self.ax.set_yscale("log")
        self.ax.set_xlim(-0.5, 12.5)
        self.ax.set_ylim(1e-9, 1e-3)
        self.ax.grid(True)
        self.ax.fill_betweenx(
            [AOI_LOWER_BOUND, AOI_UPPER_BOUND],
            [-0.5],
            [12.5],
            alpha=0.25,
            color="silver",
        )
        self.ax.tick_params(axis="both", labelsize=8)
        self.ax.set_xticks(range(0, 13))

    def plot(
        self,
        x_up: list[float],
        y_up: list[float],
        x_down: list[float],
        y_down: list[float],
    ) -> Figure:
        self.x_up = np.array(x_up)
        self.y_up = np.array(y_up)
        self.x_down = np.array(x_down)
        self.y_down = np.array(y_down)
        self.normalized_y_up = self.y_up - self.base_pressure
        self.normalized_y_down = self.y_down - self.base_pressure

        self.ax.plot(
            self.x_up,
            self.normalized_y_up,
            label="Opening",
            color="tab:blue",
            marker="o",
            markersize=2,
        )
        self.ax.plot(
            self.x_down,
            self.normalized_y_down,
            label="Closing",
            color="lightskyblue",
            marker="o",
            markersize=2,
        )
        self.ax.legend(fontsize=5)
        self.fig.tight_layout()
        self.save_figure_remotely()
        # plt.show()
        return self.fig

    def save_figure_locally(self) -> None:
        date_time: str = datetime.now().strftime("%Y-%m-%d %H_%M")
        file_name: str = f"{date_time} {self.serial_number}{self.rework_letter} Normalized Pressure vs Turns.jpg"
        results_dir: Path = Path("results")
        plot_figures_dir: str = "plot_figures"
        valve_dir: str = f"{self.serial_number}"
        folder_path: Path = results_dir / plot_figures_dir / valve_dir
        folder_path.mkdir(parents=True, exist_ok=True)
        if folder_path.exists():
            file_path: Path = folder_path / file_name
            self.fig.savefig(file_path)
        else:
            print(f"Could not save figure. {folder_path} does not exist.")

    def save_figure_remotely(self) -> None:
        date_time: str = datetime.now().strftime("%Y-%m-%d %H_%M")
        file_name: str = f"{date_time} {self.serial_number}{self.rework_letter} Normalized Pressure vs Turns.jpg"
        VAT_data_by_SN_dir: Path = Path(
            r"\\opdata2\Company\PRODUCTION FOLDER\VAT Leak Valve Test Data\VAT Data by SN"
        )
        valve_dir: str = f"{self.serial_number}"
        folder_path: Path = VAT_data_by_SN_dir / valve_dir
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            print(
                "Could not save figure to company drive. Attempting to save locally..."
            )
            self.save_figure_locally()
        if folder_path.exists():
            file_path: Path = folder_path / file_name
            self.fig.savefig(file_path)


def main() -> None:
    valve_serial_number: str = "247"
    rework_letter: str = "C"
    base_pressure: str = "1e-7"
    x_up: list[float | None] = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    y_up: list[float | None] = [
        1.2e-7,
        3.4e-7,
        4.6e-7,
        5.8e-7,
        8.5e-7,
        2.4e-6,
        5.7e-6,
        8.6e-6,
        1.3e-5,
        6e-4,
    ]
    x_down: list[float | None] = x_up
    y_down: list[float | None] = [num * 1.5 for num in y_up if num is not None]
    plot = NormalizedPlot(valve_serial_number, rework_letter, base_pressure)
    plot.plot(x_up, y_up, x_down, y_down)  # type: ignore


if __name__ == "__main__":
    main()
