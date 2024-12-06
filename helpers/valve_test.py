import time
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

    def _get_pressure(self) -> float:
        pressure, (status_code, status_string) = self.tpg.pressure_gauge()
        if status_code != 0:
            print(f'\nstatus code = {status_code}')
            print(f'\nmessage = "{status_string}"')
            print('Something went wrong reading the pressure')
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
        if self.pressure > PRESSURE_TURN_POINT:
            return True
        return False

    def _pressure_is_below_base_pressure(self) -> bool:
        if self.pressure < float(self.base_pressure):
            return True
        return False
    
    def _pressure_is_within_AOI_bounds(self) -> bool:
        if self.pressure > AOI_LOWER_BOUND and self.pressure < AOI_UPPER_BOUND:
            return True
        return False

    def _valve_is_at_zero(self) -> bool:
        valve_position = self._get_valve_position
        if valve_position == 0:
            return True
        return False
    
    def _valve_is_opening(self) -> bool:
        if self.direction == 'up':
            return True
        return False
    
    def _valve_is_closing(self) -> bool:
        if self.direction == 'down':
            return True
        return False

    def _pressure_stable(self, checklist: list[float]) -> bool:
        if len(checklist) < 2:
            return False
        percent_change = self._percent_change(checklist[0], checklist[-1])
        if percent_change < DRIFT_TOLERANCE:
            return True
        return False

    def _wait_for_stability(self, valve_position: float) -> None:
        checklist: list = []
        while not self._pressure_stable(checklist):
            for _ in range(HOLD_TIME):
                checklist.append(self.pressure)
                # ADD: record/plot valve position and pressure
                if not self._pressure_stable(checklist) and len(checklist) >= 2:
                    time.sleep(1)
                    break
                time.sleep(1)
            if self._pressure_stable(checklist):
                time.sleep(1)

    def _check_if_valve_has_reached_turn_around_point(self) -> None:
        if self._pressure_is_above_PRESSURE_TURN_POINT and self._valve_is_opening:
                self._open_valve(MICROSTEPS_PER_REV) # open valve one full turn
                time.sleep(2.5)
                # ADD: record/plot valve position and pressure
                self.direction = 'down'
                self._close_valve(MICROSTEPS_PER_REV) # close valve one full turn
                time.sleep(2.5)

    def _check_if_valve_test_needs_to_stop(self) -> None:
        if (self._valve_is_at_zero or self._pressure_is_below_base_pressure) and self._valve_is_closing:
                self.stop()
                # ADD: display a message window that says the valve test is complete.

    def _valve_should_open(self) -> bool:
        if self._valve_is_opening:
            return True
        return False

    def _open_by_STEP_SIZE_and_wait_for_stability(self) -> None:
        """
        The valve will first open by MOTOR_STEP_SIZE (typical is 1/20th of a turn of the valve) and get the valve position.
        Then the program waits for HOLD_TIME (typical is 5 seconds) before getting a pressure measurement.
        If the pressure IS NOT within the pressure area of interest then the valve position and pressure are
        recorded and the 'while self.running:' loop starts over.
        If the pressure IS within the pressure area of interest then the program waits for the pressure to stabilize
        before restarting the 'while self.running:' loop.
        """
        self._open_valve(MOTOR_STEP_SIZE)
        self.valve_position = self._get_valve_position()
        time.sleep(HOLD_TIME)
        self.pressure = self._get_pressure()
        if not self._pressure_is_within_AOI_bounds():
            # record/plot valve position and pressure
            return
        self._wait_for_stability(self.valve_position)

    def _valve_should_close(self) -> bool:
        if self.direction == 'down':
            return True
        return False

    def _close_by_STEP_SIZE_and_wait_for_stability(self) -> None:
        self._close_valve(MOTOR_STEP_SIZE)
        self.valve_position = self._get_valve_position()
        time.sleep(HOLD_TIME)
        self.pressure = self._get_pressure()
        if not self._pressure_is_within_AOI_bounds():
            # record/plot valve position and pressure
            return
        self._wait_for_stability(self.valve_position)

    @staticmethod
    def _percent_change(starting_num: float, ending_num: float) -> float:
        difference: float = ending_num - starting_num
        percent_change: float = abs(difference) / starting_num * 100
        return percent_change

    def run(self) -> None:
        self.running = True
        while self.running:
            self._check_if_valve_test_needs_to_stop()
            self._check_if_valve_has_reached_turn_around_point()
            if self._valve_should_close():
                self._close_by_STEP_SIZE_and_wait_for_stability()
            if self._valve_should_open():
                self._open_by_STEP_SIZE_and_wait_for_stability()


    def stop(self) -> None:
        self.running = False
        if int(self.motor.query_position()) != 0:
            self.motor.home_motor()
        ...