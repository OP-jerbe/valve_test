import csv
from datetime import datetime
from pathlib import Path
from matplotlib.figure import Figure
from PySide6.QtCore import QTimer, QEventLoop
from PySide6.QtWidgets import QLabel
from helpers.normalized_data_plotter import NormalizedPlot
from gui.live_plot_window import LivePlotWindow
from api.pfeiffer_tpg26x import TPG261
from api.motor import MotorController
from helpers.constants import (
    MICROSTEPS_PER_REV, HOLD_TIME, AOI_LOWER_BOUND, AOI_UPPER_BOUND, PRESSURE_TURN_POINT, MOTOR_STEP_SIZE, DRIFT_TOLERANCE
)


class ValveTest:
    def __init__(self, motor: MotorController, pressure_gauge: TPG261, serial_number: str, rework_letter: str,
                 base_pressure: str, valve_position_label: QLabel, live_plot_window: LivePlotWindow) -> None:
        self.motor: MotorController = motor
        self.tpg: TPG261 = pressure_gauge
        self.serial_number: str = serial_number
        self.rework_letter: str = rework_letter
        self.base_pressure: str = base_pressure
        self.actual_position_label: QLabel = valve_position_label
        self.live_plot_window: LivePlotWindow = live_plot_window

        self.running: bool = False
        self.direction: str = 'up'
        self.pressure: float = float(self.base_pressure)
        self.valve_position: float = int(self.motor.query_position()) / MICROSTEPS_PER_REV

        self.pressure_up_log: list[float] = list()
        self.pressure_down_log: list[float] = list()
        self.turns_up_log: list[float] = list()
        self.turns_down_log: list[float] = list()

    def _update_valve_position_label(self, valve_position: float) -> None:
        valve_position_str: str = f'{valve_position:.2f}'
        self.actual_position_label.setText(valve_position_str)

    def _get_pressure(self) -> float:
        pressure, (status_code, status_string) = self.tpg.pressure_gauge()
        if status_code != 0:
            raise ValueError(f"Pressure gauge error: {status_string}")
        return pressure

    def _get_motor_position(self) -> int:
        position: str = self.motor.query_position()
        return int(position)
    
    def _get_valve_position(self) -> float:
        motor_position: int = self._get_motor_position()
        valve_position: float = motor_position / MICROSTEPS_PER_REV
        self._update_valve_position_label(valve_position)
        return round(valve_position, 2)

    def _open_valve(self, amount: int) -> None:
        self.motor.move_relative(amount)

    def _close_valve(self, amount: int) -> None:
        self.motor.move_relative(-amount)

    def _pressure_is_above_PRESSURE_TURN_POINT(self) -> bool:
        return self.pressure > PRESSURE_TURN_POINT

    def _pressure_is_below_base_pressure(self) -> bool:
        return self.pressure < float(self.base_pressure)
    
    def _pressure_is_within_AOI_bounds(self) -> bool:
        return self.pressure > AOI_LOWER_BOUND and self.pressure < AOI_UPPER_BOUND

    def _log_turns_and_pressure(self, valve_position: float, pressure: float) -> None:
        if self.direction == 'up':
            self.turns_up_log.append(valve_position)
            self.pressure_up_log.append(pressure)
        else:
            self.turns_down_log.append(valve_position)
            self.pressure_down_log.append(pressure)

    def _pressure_stable(self, checklist: list[float]) -> bool:
        if len(checklist) < 2:
            return False
        percent_change = self._percent_change(checklist[0], checklist[-1])
        return percent_change < DRIFT_TOLERANCE

    def _wait_for_stability(self, valve_position: float) -> None:
        checklist: list[float] = []
        while not self._pressure_stable(checklist):
            for _ in range(HOLD_TIME):
                self.pressure = self._get_pressure()
                checklist.append(self.pressure)
                print(f'{checklist = }')
                self._log_turns_and_pressure(valve_position, self.pressure)
                self.live_plot_window.update_plot(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)
                if not self._pressure_stable(checklist) and len(checklist) >= 2:
                    print('Pressure not stable.\n')
                    checklist.clear()
                    self.pause(1)
                    break
                self.pause(1)
            if self._pressure_stable(checklist):
                self.pause(1)

    def _check_if_valve_has_reached_turn_around_point(self) -> None:
        if self._pressure_is_above_PRESSURE_TURN_POINT() and self.direction == 'up':
                self._open_valve(MICROSTEPS_PER_REV) # open valve one full turn
                self.pause(5)
                self.valve_position = self._get_valve_position()
                self.pressure = self._get_pressure()
                self._log_turns_and_pressure(self.valve_position, self.pressure)
                self.direction = 'down'
                self._log_turns_and_pressure(self.valve_position, self.pressure)
                self.live_plot_window.update_plot(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)
                self._close_valve(MICROSTEPS_PER_REV) # close valve one full turn
                self.pause(30)
                self.valve_position = self._get_valve_position()
                self.pressure = self._get_pressure()
                self._log_turns_and_pressure(self.valve_position, self.pressure)
                self.live_plot_window.update_plot(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)

    def _move_by_STEP_SIZE_and_wait_for_stability(self) -> None:
        if self.direction == 'up':
            self._open_valve(MOTOR_STEP_SIZE)
        else:
            self._close_valve(MOTOR_STEP_SIZE)
        self.pause(1)
        self.valve_position = self._get_valve_position()
        self.pause(HOLD_TIME-1)
        self.pressure = self._get_pressure()
        if not self._pressure_is_within_AOI_bounds():
            self._log_turns_and_pressure(self.valve_position, self.pressure)
            self.live_plot_window.update_plot(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)
            return
        self._wait_for_stability(self.valve_position)

    def _check_if_valve_test_needs_to_stop(self) -> None:
        if (self._pressure_is_below_base_pressure() or self.valve_position == 0) and self.direction == 'down':
                self.stop()
                print('Valve test complete.')
                # ADD: display a message window that says the valve test is complete.

    def _create_csv(self, file_path: Path) -> None:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Turns Up', 'Pressure Up', 'Turns Down', 'Pressure Down'])

            # Make copies of the lists
            self.turns_up_log_copy: list[float | None] = [num for num in self.turns_up_log]
            self.pressure_up_log_copy: list[float | None] = [num for num in self.pressure_up_log]
            self.turns_down_log_copy: list[float | None] = [num for num in self.turns_down_log]
            self.pressure_down_log_copy: list[float | None] = [num for num in self.pressure_down_log]

            # Ensure all list copys are the same length
            max_length = max(len(self.turns_up_log_copy), len(self.pressure_up_log_copy), len(self.turns_down_log_copy), len(self.pressure_down_log_copy))
            self.turns_up_log_copy.extend([None] * (max_length - len(self.turns_up_log)))
            self.pressure_up_log_copy.extend([None] * (max_length - len(self.pressure_up_log)))
            self.turns_down_log_copy.extend([None] * (max_length - len(self.turns_down_log)))
            self.pressure_down_log_copy.extend([None] * (max_length - len(self.pressure_down_log)))

            for row in zip(self.turns_up_log_copy, self.pressure_up_log_copy, self.turns_down_log_copy, self.pressure_down_log_copy):
                writer.writerow(row)

        print(f'CSV file saved to {file_path}')

    def save_csv_locally(self) -> None:
        date_time: str = datetime.now().strftime("%Y-%m-%d %H_%M")
        file_name: str = f'{date_time} {self.serial_number}{self.rework_letter}.csv'
        results_dir: Path = Path('results')
        csv_files_dir: str = 'csv_files'
        valve_dir: str = f'{self.serial_number}'
        folder_path: Path = results_dir / csv_files_dir / valve_dir
        folder_path.mkdir(parents=True, exist_ok=True)
        if folder_path.exists():
            file_path: Path = folder_path / file_name
            self._create_csv(file_path)
        else:
            print(f"Could not save csv file. {folder_path} does not exist")

    def save_csv_remotely(self) -> None:
        date_time: str = datetime.now().strftime("%Y-%m-%d %H_%M")
        file_name: str = f'{date_time} {self.serial_number}{self.rework_letter}.csv'
        VAT_data_by_SN_dir: Path = Path(r'\\opdata2\Company\PRODUCTION FOLDER\VAT Leak Valve Test Data\VAT Data by SN')
        valve_dir: str = f'{self.serial_number}'
        folder_path: Path = VAT_data_by_SN_dir / valve_dir
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except:
            print(f"Could not save csv file to company drive. Attempting to save locally...")
            self.save_csv_locally()
        if folder_path.exists():
            file_path: Path = folder_path / file_name
            self._create_csv(file_path)

    @staticmethod
    def _percent_change(starting_num: float, ending_num: float) -> float:
        difference: float = ending_num - starting_num
        percent_change: float = abs(difference) / starting_num * 100
        return percent_change

    @staticmethod
    def pause(seconds: float) -> None:
        loop = QEventLoop()
        QTimer.singleShot(int(seconds*1000), loop.quit)
        loop.exec()

    def plot_data(self) -> Figure:
        normalized_plot = NormalizedPlot(self.serial_number, self.rework_letter, self.base_pressure)
        figure = normalized_plot.plot(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)
        return figure

    def run(self) -> None:
        self.running = True
        while self.running:
            self._check_if_valve_has_reached_turn_around_point()
            self._move_by_STEP_SIZE_and_wait_for_stability()
            self._check_if_valve_test_needs_to_stop()
        self.save_csv_remotely()
        
    def stop(self) -> None:
        self.running = False
        if int(self.motor.query_position()) != 0:
            self.motor.home_motor()