import csv
from PySide6.QtCore import QTimer, QEventLoop
from helpers.normalized_data_plotter import NormalizedPlot
from api.pfeiffer_tpg26x import TPG261
from api.motor import MotorController
from helpers.constants import (
    MICROSTEPS_PER_REV, HOLD_TIME, AOI_LOWER_BOUND, AOI_UPPER_BOUND, PRESSURE_TURN_POINT, MOTOR_STEP_SIZE, DRIFT_TOLERANCE
)


class ValveTest:
    def __init__(self, motor: MotorController, pressure_gauge: TPG261, serial_number: str, rework_letter: str, base_pressure: str) -> None:
        self.motor: MotorController = motor
        self.tpg: TPG261 = pressure_gauge
        self.serial_number: str = serial_number
        self.rework_letter: str = rework_letter
        self.base_pressure: str = base_pressure

        self.running: bool = False
        self.direction: str = 'up'
        self.pressure: float = float(self.base_pressure)
        self.valve_position: float = int(self.motor.query_position()) / MICROSTEPS_PER_REV

        self.pressure_up_log: list[float] = list()
        self.pressure_down_log: list[float] = list()
        self.turns_up_log: list[float] = list()
        self.turns_down_log: list[float] = list()

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

    def _valve_is_at_zero(self) -> bool:
        return self._get_valve_position() == 0
    
    def _valve_is_opening(self) -> bool:
        return self.direction == 'up'
    
    def _valve_is_closing(self) -> bool:
        return self.direction == 'down'

    def _log_turns_and_pressure(self, valve_position: float, pressure: float) -> None:
        if self._valve_is_opening():
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
                if not self._pressure_stable(checklist) and len(checklist) >= 2:
                    print('Pressure not stable.\n')
                    checklist.clear()
                    self.pause(1)
                    break
                self.pause(1)
            if self._pressure_stable(checklist):
                self.pause(1)

    def _check_if_valve_has_reached_turn_around_point(self) -> None:
        if self._pressure_is_above_PRESSURE_TURN_POINT() and self._valve_is_opening():
                self._open_valve(MICROSTEPS_PER_REV) # open valve one full turn
                self.pause(5)
                self._log_turns_and_pressure(self.valve_position, self.pressure)
                self.direction = 'down'
                self._log_turns_and_pressure(self.valve_position, self.pressure)
                self._close_valve(MICROSTEPS_PER_REV) # close valve one full turn
                self.pause(5)

    def _check_if_valve_test_needs_to_stop(self) -> None:
        if (self._valve_is_at_zero() or self._pressure_is_below_base_pressure()) and self._valve_is_closing():
                self.stop()
                print('Valve test complete.')
                # ADD: display a message window that says the valve test is complete.

    def _open_by_STEP_SIZE_and_wait_for_stability(self) -> None:
        self._open_valve(MOTOR_STEP_SIZE)
        self.valve_position = self._get_valve_position()
        self.pause(HOLD_TIME)
        self.pressure = self._get_pressure()
        if not self._pressure_is_within_AOI_bounds():
            self._log_turns_and_pressure(self.valve_position, self.pressure)
            return
        self._wait_for_stability(self.valve_position)

    def _close_by_STEP_SIZE_and_wait_for_stability(self) -> None:
        self._close_valve(MOTOR_STEP_SIZE)
        self.valve_position = self._get_valve_position()
        self.pause(HOLD_TIME)
        self.pressure = self._get_pressure()
        if not self._pressure_is_within_AOI_bounds():
            self._log_turns_and_pressure(self.valve_position, self.pressure)
            return
        self._wait_for_stability(self.valve_position)

    def _create_csv(self) -> None:
        #with open(f'{self.serial_number}{self.rework_letter}.csv', mode='w', newline='') as file:
        with open(f'output.csv', mode='w', newline='') as file:
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

        print('CSV file written successfully!')

    def _plot_valve_test(self, turns_up, pressure_up, turns_down, pressure_down) -> None:
        normalized_plot = NormalizedPlot(self.serial_number, self.rework_letter, self.base_pressure)
        normalized_plot.plot(turns_up, pressure_up, turns_down, pressure_down)

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

    def run(self) -> None:
        self.running = True
        while self.running:
            self._check_if_valve_has_reached_turn_around_point()
            if self._valve_is_closing():
                self._close_by_STEP_SIZE_and_wait_for_stability()
            if self._valve_is_opening():
                self._open_by_STEP_SIZE_and_wait_for_stability()
            self._check_if_valve_test_needs_to_stop()

    def stop(self) -> None:
        self.running = False
        if int(self.motor.query_position()) != 0:
            self.motor.home_motor()
        self._create_csv()
        self._plot_valve_test(self.turns_up_log, self.pressure_up_log, self.turns_down_log, self.pressure_down_log)