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
        self._captures_taken: int = 0
        self._capture_running = True

        # sensor
        self._sensor = serial.Serial(port, baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)
        self._nsp32 = NSP32(self._sensor_data_send, self._sensor_packet_recieved)

        # recieving port thread
        self._thread = threading.Thread(target = self._sensor_data_recieve)
        self._thread.daemon = True
        self._thread.start()

        self._nsp32.GetSensorId(0)
        self._nsp32.GetWavelength(0)
    
    @property
    def captures(self):
        return self._capture_history

    def add_capture(self, data: tuple) -> None:
        self._capture_history[self._capture_index_pointer] = data
        self._capture_index_pointer = (self._capture_index_pointer + 1) % self._max_capture_history

    def test_capture(self):
        self._nsp32.AcqSpectrum(0, 1, 1, False)    # Params: (sensor ID number, integration time, frame average, auto AE)
        
    def _sensor_data_send(self, data):
        self._sensor.write(data)

    def _sensor_data_recieve(self):
        while(self._sensor.isOpen()):
            if(self._sensor.in_waiting):
                self._nsp32.OnReturnBytesReceived(self._sensor.read(self._sensor.in_waiting))

    def _sensor_packet_recieved(self, pkt: ReturnPacket) -> None:
        if pkt.CmdCode == CmdCodeEnum.GetSpectrum:
            self.add_capture(pkt.ExtractSpectrumInfo().Spectrum)
            self._captures_taken += 1
            print("Capture Added")
            if(self._captures_taken > self._max_capture_history):
                self._capture_running = False
                print("Captures complete")
            if(self._capture_running):
                self.test_capture()

def main():
    spec_data = SpectroData('/dev/ttyUSB0')
    spec_data.test_capture()
    input()
    print(spec_data.captures)
    input()



if __name__ == "__main__":
    main()
    
