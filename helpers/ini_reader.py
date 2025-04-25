import sys
from configparser import ConfigParser


def get_ini_filepath() -> str:
    if hasattr(sys, "frozen"):  # Check if running as a PyInstaller EXE
        return sys._MEIPASS + "/configuration/valve_test.ini"  # type:ignore
    else:
        return "./configuration/valve_test.ini"  # Running as a script


def load_ini(ini_file: str) -> ConfigParser:
    config_data = ConfigParser()
    config_data.read(ini_file)
    return config_data


def find_comport(config_data: ConfigParser, header: str) -> str:
    return config_data.get(header, "com_port")


def find_selection(config_data: ConfigParser, header: str, selection: str) -> str:
    return config_data.get(header, f"{selection}")
