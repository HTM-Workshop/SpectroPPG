import time
import serial
import threading
from NanoLambdaNSP32 import *

class SpectroData:
    def __init__(self, serial_device: serial.Serial, max_capture_history = 100):
        assert max_capture_history > 0
        self._max_capture_history: int = max_capture_history
        self._capture_history: list = [[] for _ in range(self._max_capture_history)]
        self._capture_index_pointer: int = 0
        self._captures_taken: int = 0
        self._capture_running = False

        # sensor
        self._sensor = serial_device
        self._nsp32 = NSP32(self._sensor_data_send, self._sensor_packet_recieved)
        self._integration_passes = 20
        self._frame_average = 1
        self._auto_ae = False

        # recieving port thread
        self._thread = threading.Thread(target = self._sensor_data_recieve)
        self._thread.daemon = True
        self._thread.start()

        # timing
        self._capture_time_history_max: int = 10
        self._capture_time_history: list = [0 for _ in range(self._capture_time_history_max)]
        self._capture_time_history_index: int = 0
        self._capture_time_average: int = 0
        self._capture_timer = 0
    

    @property
    def integration_passes(self) -> int:
        return self._integration_passes
    @integration_passes.setter
    def integration_passes(self, val: int) -> None:
        assert val > 0 and val < 100
        self._integration_passes = val
    @property
    def frame_average(self) -> int:
        return self._frame_average
    @frame_average.setter
    def frame_average(self, val: int) -> None:
        assert val > 0 and val < 100
        self._frame_average = val
    @property
    def auto_ae(self) -> bool:
        return self._auto_ae
    @auto_ae.setter
    def auto_ae(self, val: bool) -> None:
        self._auto_ae = bool(val)
    @property
    def captures(self) -> list:
        return self._capture_history
    @property
    def max_captures(self) -> int:
        return self._max_capture_history
    @property
    def capture_index(self) -> int:
        return self._capture_index_pointer
    @property
    def capture_time_ms(self) -> float:
        sps = 0
        for i in self._capture_time_history:
            sps = sps + i
        return round((sps / self._capture_time_history_max) * 1000)
    @property
    def capture_running(self) -> bool:
        return self._capture_running
    @capture_running.setter
    def capture_running(self, run: bool) -> None:
        if(not self.capture_running and run):
            self._capture_running = True
            self.test_capture()
        else:
            self._capture_running = False

    def channel_graph(self, index: int) -> list:
        channel = list()
        for i in self._capture_history:
            channel.append(i[index])
        return channel

    def add_capture(self, data: tuple) -> None:
        self._capture_history[self._capture_index_pointer] = data
        self._capture_index_pointer = (self._capture_index_pointer + 1) % self._max_capture_history

    def test_capture(self):
        self._capture_timer = time.time()
        self._nsp32.AcqSpectrum(0, self._integration_passes, self._frame_average, self._auto_ae)    # Params: (sensor ID number, integration time, frame average, auto AE)
        
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
            self._capture_time_history[self._capture_time_history_index] = time.time() - self._capture_timer
            self._capture_time_history_index = (self._capture_time_history_index + 1) % self._capture_time_history_max

            # if captures are still running, call the next capture
            if(self._capture_running):
                self.test_capture()
