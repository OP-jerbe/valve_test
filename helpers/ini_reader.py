import configparser as cp

def load_ini(ini_file: str) -> cp.ConfigParser:
     config_data = cp.ConfigParser()
     config_data.read(ini_file)
     return config_data

def find_comport(config_data: cp.ConfigParser, header: str) -> int:
    return int(config_data.get(header, 'com_port'))