import configparser as cp
import api.motor as mot
import gui.gui as gui
from api.pfeiffer_tpg26x import TPG261 as tpg


def load_ini(ini_file: str) -> cp.ConfigParser:
     config_data = cp.ConfigParser()
     config_data.read(ini_file)
     return config_data

def find_comport(config_data: cp.ConfigParser, header: str) -> str:
    return config_data.get(header, 'com_port')




def main() -> None:
    ini_file = 'valve_test.ini'
    config_data = load_ini(ini_file)
    motor_com_port = find_comport(config_data, 'Motor')
    p_gauge_com_port = find_comport(config_data, 'Pressure_Gauge')
    print(f'{motor_com_port = }')
    print(f'{p_gauge_com_port = }')

if __name__ == '__main__':
    main()

