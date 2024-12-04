
class ValveTest:
    def __init__(self, serial_number, rework_letter, base_pressure) -> None:
        self.serial_number = serial_number
        self.rework_letter = rework_letter
        self.base_pressure = base_pressure

    def run(self) -> None:
        print(f'{self.serial_number =}')
        print(f'{self.rework_letter = }')
        print(f'{self.base_pressure = }')