import serial
import time

class MotorController:
    def __init__(self, port, baud_rate=9600, address=1):
        """
        Initialize the Motor Controller.
        
        :param port: COM port for the serial connection (e.g., 'COM3').
        :param baud_rate: Baud rate for the communication (default is 9600).
        :param address: Motor controller address (default is 1).
        """
        self.port = port
        self.baud_rate = baud_rate
        self.address = address
        self.serial = serial.Serial(port, baud_rate, timeout=1)
        self.start_character = "/"
        self.end_character = "R"

    def send_command(self, command):
        """
        Send a command to the motor controller.
        
        :param command: Command string without start or end characters.
        :return: Response from the controller.
        """
        full_command = f"{self.start_character}{self.address}{command}{self.end_character}"
        self.serial.write(full_command.encode())
        time.sleep(0.1)  # Give the controller some time to respond
        return self.serial.readline().decode().strip()

    def set_current(self, running_current, holding_current):
        """
        Set the running and holding current.
        
        :param running_current: Running current percentage (0-100).
        :param holding_current: Holding current percentage (0-50).
        """
        self.send_command(f"m{running_current}")
        self.send_command(f"h{holding_current}")

    def set_velocity_and_acceleration(self, velocity, acceleration):
        """
        Set the velocity and acceleration.
        
        :param velocity: Maximum speed in microsteps per second.
        :param acceleration: Acceleration in µsteps/sec².
        """
        self.send_command(f"V{velocity}")
        self.send_command(f"L{acceleration}")

    def move_absolute(self, position):
        """
        Move motor to an absolute position.
        
        :param position: Absolute position in steps.
        """
        self.send_command(f"A{position}")

    def move_relative(self, steps):
        """
        Move motor by a relative number of steps.
        
        :param steps: Steps to move (positive for forward, negative for backward).
        """
        if steps >= 0:
            self.send_command(f"P{steps}")
        else:
            self.send_command(f"D{-steps}")

    def home_motor(self, max_steps=10000):
        """
        Home the motor to its zero position using the opto sensor.
        
        :param max_steps: Maximum steps to search for home position.
        """
        self.send_command(f"Z{max_steps}")

    def query_position(self):
        """
        Query the current motor position.
        
        :return: Motor position.
        """
        return self.send_command("?0")

    def stop(self):
        """
        Stop the current motor operation.
        """
        self.send_command("T")

    def close(self):
        """
        Close the serial connection.
        """
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
