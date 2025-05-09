from configparser import ConfigParser

try:
    from helpers.ini_reader import find_selection, get_ini_filepath, load_ini
except Exception:
    from ini_reader import find_selection, get_ini_filepath, load_ini


VERSION: str = "1.1"

ini_path: str = get_ini_filepath()

config_data: ConfigParser = load_ini(ini_path)

# Motor control constants
STEPS_PER_REV: int = 200  # Set by motor design. DO NOT CHANGE!!!
MICROSTEPS_PER_STEP: int = 1  # acceptable values are: 1, 2, 4, 8, 16, 32, 64, 128, 256 (motor velocity must be set slower, the smaller the microsteps are)
MICROSTEPS_PER_REV: int = STEPS_PER_REV * MICROSTEPS_PER_STEP
MAX_VALVE_TURNS: int = 22

# Valve test constants
VALVE_STEP_SIZE: float = float(
    find_selection(
        config_data=config_data, header="VALVE_STEP_SIZE", selection="VALVE_STEP_SIZE"
    )
)

MOTOR_STEP_SIZE: int = int(VALVE_STEP_SIZE * MICROSTEPS_PER_REV)

# The number of seconds to wait for stability
HOLD_TIME: int = int(
    find_selection(config_data=config_data, header="HOLD_TIME", selection="HOLD_TIME")
)

# The maximum percent change between pressure readings when checking for stability
DRIFT_TOLERANCE: float = float(
    find_selection(
        config_data=config_data, header="DRIFT_TOLERANCE", selection="DRIFT_TOLERANCE"
    )
)

# Window that determines if program will wait for stability set by DRIFT_TOLERANCE
AOI_LOWER_BOUND: float = float(
    find_selection(
        config_data=config_data, header="AOI_LOWER_BOUND", selection="AOI_LOWER_BOUND"
    )
)  # Pressure Area Of Interest Lower Bound
AOI_UPPER_BOUND: float = float(
    find_selection(
        config_data=config_data, header="AOI_UPPER_BOUND", selection="AOI_UPPER_BOUND"
    )
)  # Pressure Area Of Interest Upper Bound

# Pressure at which the valve should start closing
PRESSURE_TURN_POINT: float = float(
    find_selection(
        config_data=config_data,
        header="PRESSURE_TURN_POINT",
        selection="PRESSURE_TURN_POINT",
    )
)

if __name__ == "__main__":

    def print_all_ini_constants():
        print(f"{VALVE_STEP_SIZE = }")
        print(f"{HOLD_TIME = }")
        print(f"{DRIFT_TOLERANCE = }")
        print(f"{AOI_LOWER_BOUND = }")
        print(f"{AOI_UPPER_BOUND = }")
        print(f"{PRESSURE_TURN_POINT = }")

    print_all_ini_constants()
