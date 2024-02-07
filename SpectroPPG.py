import time
import threading
import serial
import serial.tools.list_ports

from NanoLambdaNSP32 import *

class SpectroData:
    def __init__(self, port, max_capture_history = 100):
        assert max_capture_history > 0
        self._max_capture_history: int = max_capture_history
        self._capture_history: list = [[] for _ in range(self._max_capture_history)]
        self._capture_index_pointer: int = 0

        # sensor
        self._sensor = serial.Serial(port, baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)
        self._nsp32 = NSP32(self._sensor_data_send, self._sensor_packet_recieved)

        # recieving port thread
        self._thread = threading.Thread(target = self._sensor_data_recieve)
        self._thread.daemon = True
        self._thread.start()

    def get_capture(self, data: tuple) -> None:
        self._capture_history[self._capture_index_pointer] = data[:]
        self._capture_index_pointer = (self._capture_index_pointer + 1) % self._max_capture_history

    def test_capture(self):
        self._nsp32.GetSensorId(0)
        self._nsp32.GetWavelength(0)
        self._nsp32.AcqSpectrum(0, 32, 3, False)	# integration time = 32; frame avg num = 3; disable AE
        
    def _sensor_data_send(self, data):
        self._sensor.write(data)

    def _sensor_data_recieve(self):
        try:
            while(self._sensor.isOpen()):
                if(self._sensor.in_waiting):
                    self._nsp32.OnReturnBytesReceived(self._sensor.read(self._sensor.in_waiting))
        except Exception as e :
            print('Data recieve error:\n' + str(e))

    def _sensor_packet_recieved(self, pkt: ReturnPacket):
        if pkt.CmdCode == CmdCodeEnum.GetSensorId :		# GetSensorId
            print('sensor id = ' + pkt.ExtractSensorIdStr())
        elif pkt.CmdCode == CmdCodeEnum.GetWavelength :	# GetWavelength
            infoW = pkt.ExtractWavelengthInfo()
            print('first element of wavelength =', infoW.Wavelength[0])
            # TODO: get more information you need from infoW
        elif pkt.CmdCode == CmdCodeEnum.GetSpectrum :	# GetSpectrum
            infoS = pkt.ExtractSpectrumInfo()
            
            print(infoS.Spectrum)
            # TODO: get more information you need from infoS


def main():
    spec_data = SpectroData('COM10')
    spec_data.test_capture()
    # press ENTER to exit the program
    input()


if __name__ == "__main__":
    main()
