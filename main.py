import sys
import time
from matplotlib.figure import Figure
from api.motor import MotorController
from api.pfeiffer_tpg26x import TPG261
from gui.gui import QApplication, MainWindow
from gui.live_plot_window import LivePlotWindow
from gui.normalized_plot_window import NormalizedPlotWindow
from helpers.constants import VERSION, MICROSTEPS_PER_STEP, MICROSTEPS_PER_REV, MAX_VALVE_TURNS
from helpers.ini_reader import load_ini, find_comport
from helpers.valve_test import ValveTest
from PySide6.QtCore import QTimer


class App:
    def __init__(self, motor_com_port: str, pressure_gauge_com_port: str) -> None:
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')

        try:
            self.motor: MotorController = self.connect_to_motor(motor_com_port)
            print("CONNECTED TO MOTOR")
        except Exception as e:
            print(f"COULD NOT CONNECT TO MOTOR\nException: {e}")
            sys.exit()
        try:
            self.pressure_gauge = TPG261(port=pressure_gauge_com_port)
            print("CONNECTED TO GAUGE\n")
        except Exception as e:
            self.pressure_gauge = None
            print(f"COULD NOT CONNECT TO PRESSURE GAUGE\nException: {e}\n")
        
        initial_motor_position: int = int(self.motor.query_position())
        initial_valve_position: float = initial_motor_position / MICROSTEPS_PER_REV
        self.gui.actual_position_reading.setText(f'{initial_valve_position:.2f}')


        self.gui.open_button.pressed.connect(self.open_button_pressed_handler)
        self.gui.open_button.released.connect(self.open_button_released_handler)
        self.gui.close_button.pressed.connect(self.close_button_pressed_handler)
        self.gui.close_button.released.connect(self.close_button_released_handler)
        self.gui.home_button.clicked.connect(self.home_button_handler)
        self.gui.set_zero_button.clicked.connect(self.set_zero_button_handler)
        self.gui.go_to_position_button.clicked.connect(self.go_to_position_button_handler)
        self.gui.go_to_position_input.returnPressed.connect(self.go_to_position_button_handler)
        self.gui.start_test_button.pressed.connect(self.start_test_button_handler)
        self.gui.stop_test_button.pressed.connect(self.stop_test_button_handler)

        self.valve_test: ValveTest | None = None

        self.gui.show()

    def open_normalized_plot_window(self, figure: Figure) -> None:
        self.normalized_plot_window = NormalizedPlotWindow(figure, parent=self.gui)
        self.normalized_plot_window.draw_figure()
        self.normalized_plot_window.show()

    def disable_gui(self) -> None:
        self.gui.open_button.setDisabled(True)
        self.gui.close_button.setDisabled(True)
        self.gui.home_button.setDisabled(True)
        self.gui.set_zero_button.setDisabled(True)
        self.gui.go_to_position_button.setDisabled(True)
        self.gui.go_to_position_input.setDisabled(True)
        self.gui.serial_number_input.setDisabled(True)
        self.gui.rework_letter_input.setDisabled(True)
        self.gui.base_pressure_input.setDisabled(True)

    def enable_gui(self) -> None:
        self.gui.open_button.setDisabled(False)
        self.gui.close_button.setDisabled(False)
        self.gui.home_button.setDisabled(False)
        self.gui.set_zero_button.setDisabled(False)
        self.gui.go_to_position_button.setDisabled(False)
        self.gui.go_to_position_input.setDisabled(False)
        self.gui.serial_number_input.setDisabled(False)
        self.gui.rework_letter_input.setDisabled(False)
        self.gui.base_pressure_input.setDisabled(False)

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
        microstep: int = MICROSTEPS_PER_STEP
        running_current: int = 100
        holding_current: int = 2
        velocity: int = 300
        acceleration: int = 50
        rotation_direction: str = 'normal'

        motor: MotorController = MotorController(port=com_port)
        motor.set_microsteps_per_step(microstep)
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
        if not self.valve_test: # if there is not a valve test running
            self.gui.start_test_button.clearFocus()
            serial_number = self.gui.serial_number_input.text()
            rework_letter = self.gui.rework_letter_input.text()
            base_pressure = self.gui.base_pressure_input.text()
            if self.pressure_gauge:
                self.live_plot_window: LivePlotWindow = LivePlotWindow(serial_number, rework_letter, base_pressure, parent=self.gui)
                self.valve_test = ValveTest(self.motor, self.pressure_gauge, serial_number, rework_letter, base_pressure, self.gui.actual_position_reading, self.live_plot_window)
                self.disable_gui()
                self.valve_test.run()
                self.enable_gui()
                self.valve_test_fig = self.valve_test.plot_data()
                self.open_normalized_plot_window(self.valve_test_fig)
                self.valve_test = None
        else:
            print("\nThere is already a valve test running.\n")

    def stop_test_button_handler(self) -> None:
        if self.valve_test and self.valve_test.running:
            self.valve_test.stop()
            self.enable_gui()
            self.open_normalized_plot_window(self.valve_test_fig)
            self.valve_test = None

    def cleanup(self) -> None:
        """
        Ensure the COM ports close and valve test is stopped when the application closes.
        """
        if self.motor:
            self.motor.close_port()
        if self.pressure_gauge:
            self.pressure_gauge.close_port()
        if self.valve_test and self.valve_test.running:
            self.valve_test.stop()
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

