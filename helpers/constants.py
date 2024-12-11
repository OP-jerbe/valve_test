try:
    from helpers.ini_reader import load_ini, find_constant
except:
    from ini_reader import load_ini, find_constant

config_data = load_ini('valve_test.ini')


VERSION: str = '1.0'

# Motor control constants
STEPS_PER_REV: int = 200 # Set by motor design do not change
MICROSTEPS_PER_STEP: int = 1 # acceptable values are: 1, 2, 4, 8, 16, 32, 64, 128, 256
MICROSTEPS_PER_REV: int = STEPS_PER_REV * MICROSTEPS_PER_STEP
MAX_VALVE_TURNS: int = 22

# Valve test constants
VALVE_STEP_SIZE: float = float(find_constant(config_data, 'VALVE_STEP_SIZE'))
MOTOR_STEP_SIZE: int = int(VALVE_STEP_SIZE * MICROSTEPS_PER_REV)
HOLD_TIME: int = int(find_constant(config_data, 'HOLD_TIME')) # the number of seconds to wait for stability
DRIFT_TOLERANCE: int = int(find_constant(config_data, 'DRIFT_TOLERANCE')) # the maximum percent change between pressure readings when checking for stability

# Window that determines if program will wait for stability set by DRIFT_TOLERANCE
AOI_LOWER_BOUND: float = float(find_constant(config_data, 'AOI_LOWER_BOUND')) # Pressure Area Of Interest Lower Bound
AOI_UPPER_BOUND: float = float(find_constant(config_data, 'AOI_UPPER_BOUND')) # Pressure Area Of Interest Upper Bound

PRESSURE_TURN_POINT: float = float(find_constant(config_data, 'PRESSURE_TURN_POINT')) # Pressure at which the valve should start closing

