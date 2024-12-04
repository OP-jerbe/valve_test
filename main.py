import sys
import time
from helpers.constants import VERSION, MICROSTEPS_PER_REV, MAX_VALVE_TURNS
from helpers.ini_reader import load_ini, find_comport
from helpers.valve_test import ValveTest
from api.motor import MotorController
from gui.gui import QApplication, MainWindow
from api.pfeiffer_tpg26x import TPG261


class App:
    def __init__(self, motor_com_port: str, pressure_gauge_com_port: str):
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')

        self.motor: MotorController = self.connect_to_motor(motor_com_port)
        initial_motor_position: int = int(self.motor.query_position())
        initial_valve_position: float = initial_motor_position / MICROSTEPS_PER_REV
        self.gui.actual_position_reading.setText(f'{initial_valve_position:.2f}')

        #self.pressure_gauge = TPG261(port=pressure_gauge_com_port)

        self.gui.open_button.pressed.connect(self.open_button_pressed_handler)
        self.gui.open_button.released.connect(self.open_button_released_handler)
        self.gui.close_button.pressed.connect(self.close_button_pressed_handler)
        self.gui.close_button.released.connect(self.close_button_released_handler)
        self.gui.home_button.clicked.connect(self.home_button_handler)
        self.gui.set_zero_button.clicked.connect(self.set_zero_button_handler)
        self.gui.go_to_position_button.clicked.connect(self.go_to_position_button_handler)
        self.gui.go_to_position_input.returnPressed.connect(self.go_to_position_button_handler)
        self.gui.start_test_button.pressed.connect(self.start_test_button_handler)

        self.gui.show()

    def _set_position_text(self) -> None:
        motor_position: str = self.motor.query_position()
        if motor_position != '':
            valve_position: float = int(motor_position) / MICROSTEPS_PER_REV
            self.gui.actual_position_reading.setText(f'{valve_position:.2f}')

    def update_valve_position_until(self, valve_set_point: float) -> None:
        motor_stop_point: int = int(valve_set_point * MICROSTEPS_PER_REV)
        motor_position: int = int(self.motor.query_position())
        valve_position: float = motor_position / MICROSTEPS_PER_REV
        while motor_position != motor_stop_point:
            time.sleep(0.25)
            motor_position: int = int(self.motor.query_position())
            valve_position: float = motor_position / MICROSTEPS_PER_REV
        self.gui.actual_position_reading.setText(f'{valve_position:.2f}')

    def connect_to_motor(self, com_port: str) -> MotorController:
        running_current: int = 100
        holding_current: int = 15
        velocity: int = 35000
        acceleration: int = 10000       
        rotation_direction: str = 'normal'

        motor: MotorController = MotorController(port=com_port)
        motor.set_current(running_current, holding_current)
        motor.set_velocity_and_acceleration(velocity, acceleration)
        motor.set_rotation_direction(rotation_direction)

        return motor

    def home_button_handler(self) -> None:
        self.motor.home_motor()
        self.update_valve_position_until(valve_set_point=0)
    
    def set_zero_button_handler(self) -> None:
        self.motor.set_zero()
        self.gui.actual_position_reading.setText('0.00')

    def open_button_pressed_handler(self) -> None:
        self.motor.move_relative(MAX_VALVE_TURNS * MICROSTEPS_PER_REV)

    def open_button_released_handler(self) -> None:
        self.motor.stop()
        self._set_position_text()

    def close_button_pressed_handler(self) -> None:
        self.motor.home_motor() # close until zero is reached

    def close_button_released_handler(self) -> None:
        self.motor.stop()
        self._set_position_text()

    def go_to_position_button_handler(self) -> None:
        if self.gui.go_to_position_input.text() != '':
            target_valve_position: float = float(self.gui.go_to_position_input.text())
            command_position: int = int(target_valve_position * MICROSTEPS_PER_REV)
            self.gui.go_to_position_input.clear()
            self.motor.move_absolute(command_position)
            self.update_valve_position_until(valve_set_point=target_valve_position)

    def start_test_button_handler(self) -> None:
        serial_number = self.gui.serial_number_input.text()
        rework_letter = self.gui.rework_letter_input.text()
        base_pressure = self.gui.base_pressure_input.text()
        valve_test = ValveTest(serial_number, rework_letter, base_pressure)
        valve_test.run()

    def cleanup(self) -> None:
        """
        Ensure the COM ports close when the application closes.
        """
        if self.motor:
            self.motor.close()
        time.sleep(0.25)
    
    def run(self) -> None:
        self.app.aboutToQuit.connect(self.cleanup)
        exit_code: int = self.app.exec()
        sys.exit(exit_code)


def main() -> None:
    ini_file: str = 'valve_test.ini'
    config_data = load_ini(ini_file)
    motor_com_port: str = find_comport(config_data, 'Motor')
    pressure_gauge_com_port: str = find_comport(config_data, 'Pressure_Gauge')
    app: App = App(motor_com_port, pressure_gauge_com_port)
    app.run()
    

if __name__ == '__main__':
    main()

