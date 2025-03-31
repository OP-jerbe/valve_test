import serial
import re

MEASUREMENT_STATUS = {
    0: 'Measurement data okay',
    1: 'Underrange',
    2: 'Overrange',
    3: 'Sensor error',
    4: 'Sensor off',
    5: 'No sensor (output: 5,2.0000E-2 [mbar])',
    6: 'Identification error',
    7: 'Error FRG'
}

class AGC100:
    """
    Class to handle communication with the AGC-100 device.
    """

    ETX = chr(3)  # \x03
    CR = chr(13) #\r
    LF = chr(10) #\n
    ENQ = chr(5)  # \x05
    ACK = chr(6)  # \x06
    NAK = chr(21)  # \x15

    def __init__(self, port: str):
        """
        Initialize communication with AGC-100.

        Args:
            port (str): Device name such as 'COM1' or '/dev/ttyUSB0'.
        """
        self.serial = serial.Serial(port=port, baudrate=9600, timeout=1)
        self.serial.write(b'\r\n')  # Equivalent to sending 'CR/LF' on initialization

    def _cr_lf(self, string):
        """Pad carriage return and line feed to a string

        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        return string + self.CR + self.LF # return '{string}\r\n'

    def _send_command(self, command):
        """Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        self.serial.write(bytes(self._cr_lf(command),'utf-8'))                 # serial.write(b'{command}\r\n')
        response = self.serial.readline().decode()
        if response == self._cr_lf(self.NAK):                                  # if response == '\x15\r\n'
            message = 'Serial communication returned negative acknowledge'
            raise IOError(message)
        elif response != self._cr_lf(self.ACK):                                # if response != '\x06\r\n'
            message = 'Serial communication returned unknown response:\n{}'\
                ''.format(repr(response))
            raise IOError(message)

    def _get_data(self):
        """Get the data that is ready on the device

        :returns: the raw data
        :rtype:str
        """
        self.serial.write(bytes(self.ENQ,'utf-8')) # serial.write(b'\x05')
        data = self.serial.readline().decode()
        return data.rstrip(self.LF).rstrip(self.CR)

    def pressure_gauge(self) -> tuple[float, int]:
        """
        Get pressure reading from AGC-100.

        Returns:
            tuple: (pressure value, status indicator)
        """
        if not self.serial.is_open:
            raise ValueError("Serial port is not open!")

        # Send 'PR1' command and read response
        self.serial.write(b'PR1\r\n')
        ret = self.serial.readline().decode().strip()

        # Check for positive acknowledgment (hex '6')
        if ret and ret[0] == '6':
            # Send 'CTRL-E' (hex 0x05) without termination and read with termination
            self.serial.write(b'\x05')
            ret = self.serial.readline().decode().strip()
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
        if self.serial.is_open:
            self.serial.close()

# Example usage:
# agc = AGC100('COM1')
# pressure, status = agc.get_pressure()
# agc.close()
