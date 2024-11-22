import serial
import time

class MotorController:
    def __init__(self, port, baud_rate=9600, address=1):
        """
        Initialize the Motor Controller.
        
        :param port: COM port for the serial connection (e.g., '3' or 3).
        :type port: str or int
        :param baud_rate: Baud rate for the communication (default is 9600).
        :param address: Motor controller address (default is 1).
        """
        self.port = port
        self.baud_rate = baud_rate
        self.address = address
        self.serial = serial.Serial(port, baud_rate, timeout=1)
        self.start_character = "/"
        self.end_character = "R"
        self.carriage_return = "\r"

    def send_command(self, command):
        """
        Send a command to the motor controller.
        
        :param command: Command string without start or end characters.
        :return: Response from the controller.
        """
        full_command = f"{self.start_character}{self.address}{command}{self.end_character}{self.carriage_return}"
        self.serial.write(full_command.encode())
        print(f'{full_command = }')
        time.sleep(0.1)  # Give the controller some time to respond
        raw_response = self.serial.readline()
        decoded_response = raw_response.decode(errors='ignore').strip()
        text = str(decoded_response)[3:-1]
        print(f'{raw_response = }')
        print(f'{decoded_response = }')
        print(f'{text = }\n')
        return text

    def set_current(self, running_current, holding_current) -> None:
        """
        Set the running and holding current.
        
        :param running_current: Running current percentage (0-100).
        :param holding_current: Holding current percentage (0-50).
        """
        print("Running Current Command".upper())
        self.send_command(f"m{running_current}")
        print("Holding Current Command".upper())
        self.send_command(f"h{holding_current}")

    def set_velocity_and_acceleration(self, velocity, acceleration) -> None:
        """
        Set the velocity and acceleration.
        
        :param velocity: Maximum speed in microsteps per second.
        :param acceleration: Acceleration in µsteps/sec².
        """
        print("Velocity Command".upper())
        self.send_command(f"V{velocity}")
        print("Acceleration Command".upper())
        self.send_command(f"L{acceleration}")

    def move_absolute(self, position) -> None:
        """
        Move motor to an absolute position.
        
        :param position: Absolute position in steps.
        """
        print("Absolute Movement Command".upper())
        self.send_command(f"A{position}")

    def move_relative(self, steps) -> None:
        """
        Move motor by a relative number of steps.
        
        :param steps: Steps to move (positive for forward, negative for backward).
        """
        print("Relative Movement Command".upper())
        if steps >= 0:
            self.send_command(f"P{steps}")
        else:
            self.send_command(f"D{-steps}")

    def home_motor(self) -> None:
        """
        Command the motor to go to its zero position
        """
        print("Home Command".upper())
        self.send_command("A0")

    def query_position(self) -> str:
        """
        Query the current motor position.
        
        :return: Motor position.
        """
        print("Query Position Command".upper())
        return self.send_command("?0")
    
    def set_zero(self) -> None:
        """
        Set the current position to zero without moving the motor.
        """
        print("Set Zero Command".upper())
        self.send_command('z')

    def set_rotation_direction(self, direction: str='normal') -> None:
        """
        Switches the motors rotation direction. The P and D command will switch directions.

        :param direction: Motor operation direction ('normal' for ccw open, 'reverse' for cw to open.)
        """
        print("Rotation Direction Command".upper())
        if direction == 'normal':
            self.send_command("F0")
        elif direction == 'reverse':
            self.send_command("F1")
        else:
            # raise an exception here
            return

    def stop(self):
        """
        Stop the current motor operation.
        """
        print("Stop Command".upper())
        self.send_command("T")

    def close(self):
        """
        Close the serial connection.
        """
        print("Close Port Command".upper())
        self.serial.close()

# Example usage in main.py:
if __name__ == "__main__":
    motor = MotorController(port="COM3", baud_rate=9600, address=1)
    try:
        motor.set_current(running_current=50, holding_current=20)
        motor.set_velocity_and_acceleration(velocity=2000, acceleration=5000)
        motor.home_motor()
        motor.move_relative(1000)
        print("Current Position:", motor.query_position())
    finally:
        motor.stop()
        motor.close()
