import csv
import sys
import time
import xlwt
import numpy
import serial
import serial.tools.list_ports
import threading
import pyqtgraph as pg
from scipy.signal import savgol_filter
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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow, SpectroData):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle(f"SpectroPPG - ALPHA")

        self._spec_data: SpectroData = None
        self._running: bool = False

        # graph properties
        self.graph.disableAutoRange()
        self.graph.showGrid(True, True, alpha = 0.5)
        self.graph_padding_factor = 0.667
        self.green_pen = pg.mkPen('g', width = 2)
        self.red_pen = pg.mkPen('r', width = 2)

        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.update_graph)
        self.graph_frame_rate = 10
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))

        # channel graph timer
        self.channel_graph_frame_rate = 1
        self.channel_timer_ms = int(1 / (self.channel_graph_frame_rate / 1000))
        self.channel_timer = QtCore.QTimer()
        self.channel_timer.timeout.connect(self.channel_graph_update)


        # ui handlers
        self.channel_slider.valueChanged.connect(self.update_channel_ui)
        self.button_refresh.clicked.connect(self.ser_com_refresh)
        self.button_connect.clicked.connect(self.serial_connect)
        self.button_startstop.clicked.connect(self.startstop)
        self.button_update_sensor.clicked.connect(self.update_sensor)
        self.button_export_channel.clicked.connect(self.export_channel_csv)
        self.button_export_all.clicked.connect(self.export_all_csv)

        self.ser_com_refresh()


    def update_graph(self):
        self.graph.clear()
        capture = self._spec_data.captures[self._spec_data.capture_index - 1]
        self.graph.plot(numpy.arange(len(capture)), capture, pen = self.green_pen, skipFiniteCheck = True)
        self.graph.enableAutoRange()
        self.graph.disableAutoRange()
        line = pg.InfiniteLine(pos = self.channel_slider.value(), pen = self.red_pen, angle = 90, movable = False)
        self.graph.addItem(line)

    def channel_graph_update(self):
        if(self._spec_data.capture_running):
            self.label_3.setText(f"Average Capture Time (ms): {self._spec_data.capture_time_ms}")
            try:
                self.label_capture_ps.setText(f"Captures per second: {1000 / self._spec_data.capture_time_ms:.2f}")
            except ZeroDivisionError as e:
                print(e)
        self.graph_2.clear()
        if(self.checkBox_savgol_enable.isChecked()):
            pass
        else:
            try:
                channel = self._spec_data.channel_graph(self.channel_slider.value())
                self.graph_2.plot(numpy.arange(len(channel)), channel, pen = self.green_pen, skipFiniteCheck = True)
                self.graph_2.enableAutoRange()
                self.graph_2.disableAutoRange()
            except IndexError as e:      # the internal data is still building up, so we can safely pass this
                print(e)

    def serial_connect(self):
        if(self._spec_data is None):
            port = self.port_dropdown.itemData(self.port_dropdown.currentIndex())
            com_port = serial.Serial(port, baudrate = 115200, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)
            self._spec_data = SpectroData(com_port)
            self.button_connect.setText("Disconnect")
            self.button_startstop.setEnabled(True)
            self.channel_timer.start(self.channel_timer_ms)
            self.graph_timer.start(self.graph_timer_ms)
        else:
            self.channel_timer.stop()
            self.graph_timer.stop()
            del self._spec_data
            self._spec_data = None
            self.button_startstop.setEnabled(False)
            self.button_connect.setText("Connect")
    
    def startstop(self):
        if(not self._spec_data.capture_running):
            self._spec_data.capture_running = True
            self.button_startstop.setText("Stop")
            self.button_connect.setEnabled(False)
        else:
            self._spec_data.capture_running = False
            self.button_startstop.setText("Start")
            self.button_connect.setEnabled(True)

    def update_channel_ui(self):
        self.channel_lcd.display(self.channel_slider.value())

    def update_sensor(self):
        self._spec_data.auto_ae = self.checkbox_auto_ae.isChecked()
        self._spec_data.integration_passes = self.spinbox_int_passes.value()
        self._spec_data.frame_average = self.spinbox_frame_avg.value()

    def export_channel_csv(self):
        default_filename = str(time.time()).split('.', maxsplit=1)[0] + '.csv'
        channel = self.channel_slider.value()
        try:
            csv_file = open(default_filename, 'w', newline = '')
            writer = csv.writer(csv_file)
            writer.writerow(self._spec_data.channel_graph(channel))
            csv_file.flush()
            csv_file.close()
            self.ui_display_error_message("Export", "Export Successful")
        except Exception as e:
            self.ui_display_error_message("Export Error", e)

    def export_all_csv(self):
        default_filename = str(time.time()).split('.', maxsplit=1)[0] + '.xls'
        xls = xlwt.Workbook()
        sheet = xls.add_sheet("Test Results")
        data = self._spec_data.captures
        for i in range(len(data)):
            for j in range(len(data[i])):
                sheet.write(i, j, data[i][j])
        xls.save(default_filename)



    # refresh available devices, store in dropdown menu storage
    def ser_com_refresh(self):
        """
        Refreshes the list of available serial devices.\n
        Results are stored in the dropdown menu.\n
        Uses addItem to store the device string."""
        self.port_dropdown.clear()
        available_ports = serial.tools.list_ports.comports()
        for device in available_ports:
            d_name = device.device + ": " + device.description
            self.port_dropdown.addItem(d_name, device.device)

    def ui_display_error_message(self, title: str, msg: str) -> None:
        """Display a generic error message to the user."""
        error_message = QtWidgets.QMessageBox()
        error_message.setWindowTitle(title)
        error_message.setText(str(msg))
        error_message.exec_()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
    
