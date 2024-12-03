import traceback
import threading
import time
from api.motor import MotorController
from PySide6.QtCore import Signal
from helpers.constants import MICROSTEPS_PER_REV


class PositionAcquisition():
    def __init__(self, motor: MotorController, update_callback, interval: float | int = 1) -> None:
        super().__init__()
        self.motor: MotorController = motor
        self.update_callback = update_callback
        self.interval: float | int = interval
        self.running: bool = False

        self.acq_thread: threading.Thread | None = None

    def start(self) -> None:
        """
        Start the position acquisition process.
        """
        if not self.running:
            self.running = True
            self.acq_thread = threading.Thread(target=self._run)
            self.acq_thread.start()
            print("Started threading.\n")

    def stop(self) -> None:
        """ 
        Stop the position acquisition process
        """
        self.running = False
        if self.acq_thread is not None:
            self.acq_thread.join()
            print("Stopped threading.\n")

    def _run(self) -> None:
        """
        Run the data acquisition loop in the background.
        """
        while self.running:
            self._fetch_data()
            time.sleep(self.interval)

    def _fetch_data(self) -> None:
        """
        Fetch data from the motor and update the position
        """
        if not self.motor:
            return
        
        try:
            motor_position: str = self.motor.query_position()
            valve_position: float = int(motor_position) / MICROSTEPS_PER_REV
            self.update_callback(valve_position)
        except Exception as e:
            traceback.print_exc()
            print(f'\nError while fetching data: {e}\n')