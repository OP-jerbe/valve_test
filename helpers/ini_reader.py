import configparser as cp
import sys

def get_ini_filepath() -> str:
     if hasattr(sys, 'frozen'):  # Check if running as a PyInstaller EXE
          return sys._MEIPASS + '/configuration/valve_test.ini' # type:ignore
     else:
          return './configuration/valve_test.ini'  # Running as a script

def load_ini(ini_file: str) -> cp.ConfigParser:
     config_data = cp.ConfigParser()
     config_data.read(ini_file)
     return config_data

def find_comport(config_data: cp.ConfigParser, header: str) -> str:
    return config_data.get(header, 'com_port')

def find_selection(config_data: cp.ConfigParser, header: str, selection: str) -> str:
     return config_data.get(header, f'{selection}')