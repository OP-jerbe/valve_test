from api.pfeiffer_tpg26x import TPG261


class ValveTest:
    def __init__(self, pressure_gauge: TPG261, serial_number: str, rework_letter: str, base_pressure: str) -> None:
        self.pressure_gauge = pressure_gauge
        self.serial_number = serial_number
        self.rework_letter = rework_letter
        self.base_pressure = base_pressure

    

    def run(self) -> None:
        print(f'{self.serial_number =}')
        print(f'{self.rework_letter = }')
        print(f'{self.base_pressure = }')