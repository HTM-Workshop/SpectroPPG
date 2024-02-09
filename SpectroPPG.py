import sys
import time
import numpy
import serial
import serial.tools.list_ports
import threading
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtWidgets, QtGui

# manual includes to fix occasional compile problem
try:
    from pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 import *
    from pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5 import *
    from pyqtgraph.imageview.ImageViewTemplate_pyqt5 import *
    from pyqtgraph.console.template_pyqt5 import *
except:
    pass

from test_ui import Ui_MainWindow
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

        # timing
        self._capture_time_history_max: int = 10
        self._capture_time_history: list = [0 for _ in range(self._capture_time_history_max)]
        self._capture_time_history_index: int = 0
        self._capture_time_average: int = 0
        self._capture_timer = 0

        self._nsp32.GetSensorId(0)
        self._nsp32.GetWavelength(0)
    
    @property
    def captures(self):
        return self._capture_history
    @property
    def max_captures(self):
        return self._max_capture_history
    @property
    def capture_index(self):
        return self._capture_index_pointer
    @property
    def capture_time_ms(self):
        sps = 0
        for i in self._capture_time_history:
            sps = sps + i
        return round((sps / self._capture_time_history_max) * 1000)
    
    def channel_graph(self, index: int):
        channel = list()
        for i in self._capture_history:
            channel.append(i[index])
        return channel

    def add_capture(self, data: tuple) -> None:
        self._capture_history[self._capture_index_pointer] = data
        self._capture_index_pointer = (self._capture_index_pointer + 1) % self._max_capture_history

    def test_capture(self):
        self._capture_timer = time.time()
        self._nsp32.AcqSpectrum(0, 20, 1, False)    # Params: (sensor ID number, integration time, frame average, auto AE)
        
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
            if(self._capture_running):
                self.test_capture()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, SpectroData):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle(f"SpectroPPG")

        self._spec_data = SpectroData('/dev/ttyUSB0')
        self._spec_data.test_capture()

        # graph properties
        self.graph.disableAutoRange()
        self.graph.showGrid(True, True, alpha = 0.5)
        self.graph_padding_factor = 0.667
        self.green_pen = pg.mkPen('g', width = 2)
        self.red_pen = pg.mkPen('r', width = 2)

        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.update_graph)
        self.graph_frame_rate = 5
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))
        self.graph_timer.start(self.graph_timer_ms)

        # channel graph timer
        self.channel_graph_frame_rate = 1
        self.channel_timer = QtCore.QTimer()
        self.channel_timer.timeout.connect(self.channel_graph_update)
        self.channel_timer.start(int(1 / (self.channel_graph_frame_rate / 1000)))

        # channel ui handler
        self.channel_slider.valueChanged.connect(self.update_channel_ui)


    def update_graph(self):
        self.graph.clear()
        capture = self._spec_data.captures[self._spec_data.capture_index - 1]
        self.graph.plot(numpy.arange(len(capture)), capture, pen = self.green_pen, skipFiniteCheck = True)
        self.graph.enableAutoRange()
        self.graph.disableAutoRange()
        line = pg.InfiniteLine(pos = self.channel_slider.value(), pen = self.red_pen, angle = 90, movable = False)
        self.graph.addItem(line)

    def channel_graph_update(self):
        try:
            self.label_3.setText(f"Average Capture Time (ms): {self._spec_data.capture_time_ms}")
            self.label_capture_ps.setText(f"Captures per second: {1000 / self._spec_data.capture_time_ms:.2f}")
            self.graph_2.clear()
            channel = self._spec_data.channel_graph(self.channel_slider.value())
            self.graph_2.plot(numpy.arange(len(channel)), channel, pen = self.green_pen, skipFiniteCheck = True)
            self.graph_2.enableAutoRange()
            self.graph_2.disableAutoRange()
        except IndexError:
            pass

    def update_channel_ui(self):
        self.channel_lcd.display(self.channel_slider.value())


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
    
