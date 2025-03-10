import serial
import re

class AGC100:
    """
    Class to handle communication with the AGC-100 device.
    """

    def __init__(self, port: str):
        """
        Initialize communication with AGC-100.

        Args:
            port (str): Device name such as 'COM1' or '/dev/ttyUSB0'.
        """
        self.serial_conn = serial.Serial(port=port, baudrate=9600, timeout=1)
        self.serial_conn.write(b'\r\n')  # Equivalent to sending 'CR/LF' on initialization

    def pressure_gauge(self) -> tuple[float, int]:
        """
        Get pressure reading from AGC-100.

        Returns:
            tuple: (pressure value, status indicator)
        """
        if not self.serial_conn.is_open:
            raise ValueError("Serial port is not open!")

        # Send 'PR1' command and read response
        self.serial_conn.write(b'PR1\r\n')
        ret = self.serial_conn.readline().decode().strip()

        # Check for positive acknowledgment (hex '6')
        if ret and ret[0] == '6':
            # Send 'CTRL-E' (hex 0x05) without termination and read with termination
            self.serial_conn.write(b'\x05')
            ret = self.serial_conn.readline().decode().strip()
        else:
            raise ValueError("Positive ACK not received!")

        # Parse response
        match = re.search(r'(\d), ([\deE+.-]+)', ret)
        if match:
            stat = int(match.group(1))
            p = float(match.group(2))
            return p, stat
        else:
            raise ValueError("Response in unexpected format!")

    def close_port(self) -> None:
        """
        Terminate serial communication with AGC-100.
        """
        if self.serial_conn.is_open:
            self.serial_conn.close()

# Example usage:
# agc = AGC100('COM1')
# pressure, status = agc.get_pressure()
# agc.close()
