import sys
from helpers.ini_reader import load_ini, find_comport
from api.motor import MotorController as mc
from gui.gui import QApplication, MainWindow
from api.pfeiffer_tpg26x import TPG261 as tpg

VERSION = '1.0'

class App:
    def __init__(self, motor_com_port: int, pressure_gauge_com_port: int):
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')
        self.motor_com_port = motor_com_port
        self.pressure_gauge_com_port = pressure_gauge_com_port


        self.gui.show()

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

