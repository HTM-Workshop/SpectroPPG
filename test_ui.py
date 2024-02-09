# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(652, 419)
        MainWindow.setMinimumSize(QtCore.QSize(652, 419))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setMinimumSize(QtCore.QSize(137, 24))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_capture_ps = QtWidgets.QLabel(self.centralwidget)
        self.label_capture_ps.setObjectName("label_capture_ps")
        self.horizontalLayout_4.addWidget(self.label_capture_ps)
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 6, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_channel = QtWidgets.QLabel(self.centralwidget)
        self.label_channel.setAlignment(QtCore.Qt.AlignCenter)
        self.label_channel.setObjectName("label_channel")
        self.horizontalLayout_3.addWidget(self.label_channel)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graph_2 = PlotWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph_2.sizePolicy().hasHeightForWidth())
        self.graph_2.setSizePolicy(sizePolicy)
        self.graph_2.setMinimumSize(QtCore.QSize(0, 0))
        self.graph_2.setObjectName("graph_2")
        self.horizontalLayout.addWidget(self.graph_2)
        self.graph = PlotWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graph.sizePolicy().hasHeightForWidth())
        self.graph.setSizePolicy(sizePolicy)
        self.graph.setMinimumSize(QtCore.QSize(0, 0))
        self.graph.setObjectName("graph")
        self.horizontalLayout.addWidget(self.graph)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setMinimumSize(QtCore.QSize(86, 27))
        self.pushButton.setMaximumSize(QtCore.QSize(86, 27))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.channel_slider = QtWidgets.QSlider(self.frame)
        self.channel_slider.setMaximum(135)
        self.channel_slider.setSliderPosition(60)
        self.channel_slider.setOrientation(QtCore.Qt.Horizontal)
        self.channel_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.channel_slider.setObjectName("channel_slider")
        self.horizontalLayout_2.addWidget(self.channel_slider)
        self.channel_lcd = QtWidgets.QLCDNumber(self.frame)
        self.channel_lcd.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.channel_lcd.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.channel_lcd.setSmallDecimalPoint(False)
        self.channel_lcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.channel_lcd.setProperty("value", 60.0)
        self.channel_lcd.setObjectName("channel_lcd")
        self.horizontalLayout_2.addWidget(self.channel_lcd)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_3.setText(_translate("MainWindow", "Capture time avg (ms): 000"))
        self.label_capture_ps.setText(_translate("MainWindow", "Captures per second:  00"))
        self.label_channel.setText(_translate("MainWindow", "Channel History"))
        self.label.setText(_translate("MainWindow", "Live Spectrum"))
        self.pushButton.setText(_translate("MainWindow", "Start"))
        self.label_2.setText(_translate("MainWindow", "Channel Select:"))
from pyqtgraph import PlotWidget
