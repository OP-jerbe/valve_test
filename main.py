import sys
import time
from PySide6.QtCore import QTimer
from helpers.position_acquisition import PositionAcquisition
from helpers.ini_reader import load_ini, find_comport
from helpers.manual_motor_control import ContinuousMotorControl as cmc
from api.motor import MotorController
from gui.gui import QApplication, MainWindow
from api.pfeiffer_tpg26x import TPG261

VERSION: str = '1.0'
STEPS_PER_REV: int = 200
MICROSTEPS_PER_STEP: int = 256
MICROSTEPS_PER_REV: int = STEPS_PER_REV * MICROSTEPS_PER_STEP
MAX_VALVE_TURNS: int = 22

class App:
    def __init__(self, motor_com_port: str, pressure_gauge_com_port: str):
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')

        self.motor: MotorController = self.connect_to_motor(motor_com_port)
        self.initial_position: str = self.motor.query_position()
        self.gui.actual_position_reading.setText(str(self.initial_position))
        
        self.timer = QTimer(self.gui)
        self.timer.timeout.connect(self.update_display)
        self.refresh_rate = 500
        self.timer.start(self.refresh_rate)
        self.position_acquisition = PositionAcquisition(self.motor, self.refresh_rate / 1000)
        self.position_acquisition.start()

        #self.pressure_gauge = TPG261(port=pressure_gauge_com_port)

        self.gui.open_button.pressed.connect(self.open_button_pressed_handler)
        self.gui.open_button.released.connect(self.open_button_released_handler)
        self.gui.close_button.pressed.connect(self.close_button_pressed_handler)
        self.gui.close_button.released.connect(self.close_button_released_handler)
        self.gui.home_button.clicked.connect(self.home_button_handler)
        self.gui.set_zero_button.clicked.connect(self.set_zero_button_handler)
        self.gui.go_to_position_button.clicked.connect(self.go_to_position_button_handler)

        self.gui.show()

    def connect_to_motor(self, com_port: str) -> MotorController:
        running_current: int = 100
        holding_current: int = 15
        velocity: int = 35000
        acceleration: int = 10000       
        rotation_direction: str = 'normal'

        motor = MotorController(port=com_port)
        motor.set_current(running_current, holding_current)
        motor.set_velocity_and_acceleration(velocity, acceleration)
        motor.set_rotation_direction(rotation_direction)

        return motor

    def update_display(self) -> None:
        position = self.position_acquisition.get_position()
        print(f'update display position = {position}\n')
        self.gui.actual_position_reading.setText(position)

    def home_button_handler(self) -> None:
        self.motor.home_motor()
    
    def set_zero_button_handler(self) -> None:
        self.motor.set_zero()

    def open_button_pressed_handler(self) -> None:
        self.motor.move_relative(MAX_VALVE_TURNS * MICROSTEPS_PER_REV)

    def open_button_released_handler(self) -> None:
        self.motor.stop()

    def close_button_pressed_handler(self) -> None:
        self.motor.home_motor() # close until zero is reached

    def close_button_released_handler(self) -> None:
        self.motor.stop()

    def go_to_position_button_handler(self) -> None:
        target_position = self.gui.go_to_position_input.text()
        command_position = int(float(target_position) * MICROSTEPS_PER_REV)
        self.motor.move_absolute(command_position)
        self.gui.go_to_position_input.clear()

    def run(self) -> None:
        exit_code: int = self.app.exec()
        sys.exit(exit_code)


def main() -> None:
    ini_file = 'valve_test.ini'
    config_data = load_ini(ini_file)
    motor_com_port = find_comport(config_data, 'Motor')
    pressure_gauge_com_port = find_comport(config_data, 'Pressure_Gauge')
    app = App(motor_com_port, pressure_gauge_com_port)
    app.run()

if __name__ == '__main__':
    main()

