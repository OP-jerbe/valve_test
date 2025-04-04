import serial

MEASUREMENT_STATUS: dict = {
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

    ETX: str = chr(3)  # \x03
    CR: str = chr(13)  #\r
    LF: str = chr(10)  #\n
    ENQ: str = chr(5)  # \x05
    ACK: str = chr(6)  # \x06
    NAK: str = chr(21) # \x15

    def __init__(self, port: str='/dev/ttyUSB0', baudrate: int=9600) -> None:
        """
        Initialize communication with AGC-100.

        Args:
            port (str): Device name such as 'COM1' or '/dev/ttyUSB0'.
        """
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1)

    def _cr_lf(self, string: str) -> str:
        """
        Pad carriage return and line feed to a string

        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        return string + self.CR + self.LF # return '{string}\r\n'

    def _send_command(self, command: str) -> None:
        """
        Send a command and check if it is positively acknowledged

        :param command: The command to send
        :type command: str
        :raises IOError: if the negative acknowledged or a unknown response
            is returned
        """
        self.serial.write(bytes(self._cr_lf(command),'utf-8'))                # serial.write(b'{command}\r\n')
        response: str = self.serial.readline().decode()
        if response == self._cr_lf(self.NAK):                                  # if response == '\x15\r\n'
            message = 'Serial communication returned negative acknowledge'
            raise IOError(message)
        elif response != self._cr_lf(self.ACK):                                # if response != '\x06\r\n'
            message = 'Serial communication returned unknown response:\n{}'\
                ''.format(repr(response))
            raise IOError(message)

    def _get_data(self) -> str:
        """
        Get the data that is ready on the device

        :returns: the raw data
        :rtype:str
        """
        self.serial.write(bytes(self.ENQ,'utf-8')) # serial.write(b'\x05')
        data: str = self.serial.readline().decode()
        return data.rstrip(self.LF).rstrip(self.CR)

    def pressure_gauge(self, gauge=1) -> tuple[float, tuple[int, str]]:
        """
        Return the pressure measured by gauge X

        :param gauge: The gauge number, 1 or 2
        :type gauge: int
        :raises ValueError: if gauge is not 1 or 2
        :return: (value, (status_code, status_message))
        :rtype: tuple
        """

        if gauge not in [1, 2]:
            message = 'The input gauge number can only be 1 or 2'
            raise ValueError(message)
        self._send_command('PR' + str(gauge))
        reply = self._get_data()
        status_code = int(reply.split(',')[0])
        value = float(reply.split(',')[1])
        return value, (status_code, MEASUREMENT_STATUS[status_code])

    def close_port(self) -> None:
        """
        Terminate serial communication with AGC-100.
        """
        self.serial.close()
        if self.serial.is_open is not True:
            print('Pressure gauge serial port closed.')


# Example usage:
# agc = AGC100('COM1')
# pressure, (status_code, MEASUREMENT_STATUS[status_code]) = agc.pressure_gauge()
# agc.close_port()
