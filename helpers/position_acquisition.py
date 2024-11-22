import traceback
import threading
import time
from api.motor import MotorController
from PySide6.QtCore import Signal


class PositionAcquisition():
    def __init__(self, motor: MotorController, interval: float | int = 1) -> None:
        super().__init__()
        self.motor: MotorController = motor
        self.interval: float | int = interval
        self.running: bool = False

        self.position: str = ''

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
            print("Stopped threading.\n")
            self.acq_thread.join()

    def _run(self) -> None:
        """
        Run the data acquisition loop in the background.
        """
        while self.running:
            print('Trying to fetch data...\n')
            self._fetch_data()
            time.sleep(self.interval)

    def _fetch_data(self) -> None:
        """
        Fetch data from the motor and update the position
        """
        if not self.motor:
            return
        
        try:
            print('Fetching data...\n')
            self.position: str = self.motor.query_position()
            print(f'Current position = {self.position}\n')
        except Exception as e:
            traceback.print_exc()
            print(f'\nError while fetching data: {e}\n')

    def get_position(self) -> str:
        """
        Get the latest fetched position.

        :return: A string with the motor position
        """
        print("Getting latest position...\n")
        return self.position