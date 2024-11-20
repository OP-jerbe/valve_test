import sys
from helpers.ini_reader import load_ini, find_comport
from api.motor import MotorController as mc
from gui.gui import QApplication, MainWindow
from api.pfeiffer_tpg26x import TPG261 as tpg

VERSION = '1.0'

class App:
    def __init__(self):
        self.app = QApplication([])
        self.gui = MainWindow()
        self.gui.setWindowTitle(f'Automated Valve Test v{VERSION}')


        self.gui.show()

    def run(self) -> None:
        exit_code: int = self.app.exec()
        sys.exit(exit_code)


def main() -> None:
    ini_file = 'valve_test.ini'
    config_data = load_ini(ini_file)
    motor_com_port = find_comport(config_data, 'Motor')
    p_gauge_com_port = find_comport(config_data, 'Pressure_Gauge')

    print(f'{motor_com_port = }')
    print(f'{p_gauge_com_port = }')

    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

def main2() -> None:
    app = App()
    app.run()

if __name__ == '__main__':
    main2()

