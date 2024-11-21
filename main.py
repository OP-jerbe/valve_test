import sys
import time
from PySide6.QtCore import QTimer
from helpers.ini_reader import load_ini, find_comport
from helpers.manual_motor_control import ContinuousMotorControl as cmc
from api.motor import MotorController
from gui.gui import QApplication, MainWindow
from api.pfeiffer_tpg26x import TPG261

VERSION = '1.0'

class App:
    def __init__(self, motor_com_port: str, pressure_gauge_com_port: str):
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')

        self.motor = self.connect_to_motor(motor_com_port, 100, 15, 35000, 10)
        self.initial_position = self.motor.query_position()
        self.gui.actual_position_reading.setText(str(self.initial_position))
        
        #self.pressure_gauge = TPG261(port=pressure_gauge_com_port)

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_motor)

        self.direction: str | None = None

        self.gui.open_button.pressed.connect(self.start_counterclockwise_motor)
        self.gui.open_button.released.connect(self.stop_motor)
        self.gui.close_button.pressed.connect(self.start_clockwise_motor)
        self.gui.close_button.released.connect(self.stop_motor)
        self.gui.home_button.clicked.connect(self.home_button_handler)
        self.gui.set_zero_button.clicked.connect(self.set_zero_button_handler)
        self.gui.go_to_position_button.clicked.connect(self.go_to_position_button_handler)

        self.gui.show()

    def connect_to_motor(self, com_port: str, running_current: int, holding_current: int, velocity: int, acceleration: int) -> MotorController:
        motor = MotorController(port=com_port)
        motor.set_current(running_current, holding_current)
        motor.set_velocity_and_acceleration(velocity, acceleration)
        return motor

    def home_button_handler(self) -> None:
        self.motor.home_motor()
    
    def set_zero_button_handler(self) -> None:
        self.motor.set_zero()

    def go_to_position_button_handler(self) -> None:
        target_position = self.gui.go_to_position_input.text()
        command_position = int(float(target_position) * 51200)
        self.motor.move_absolute(command_position)
        self.gui.go_to_position_input.clear()

    def start_clockwise_motor(self) -> None:
        self.direction = 'clockwise'
        print('Motor moving clockwise')
        self.move_timer.start(100)

    def start_counterclockwise_motor(self) -> None:
        self.direction = 'counterclockwise'
        print("Motor moving counterclockwise")
        self.move_timer.start(100)
    
    def stop_motor(self) -> None:
        print("Motor stopped")
        self.move_timer.stop()
        self.direction = None

    def move_motor(self) -> None:
        if self.direction == 'clockwise':
            print("Motor is moving clockwise...")
            self.motor.move_relative(1000)
        elif self.direction == 'counterclockwise':
            print("Motor is moving counterclockwise...")
            self.motor.move_relative(-1000)
        else:
            print("No direction set")

    def update_position_reading(self) -> None:
        position = self.motor.query_position()
        self.gui.actual_position_reading.setText(position)

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

