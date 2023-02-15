from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from msg_def import *
from my_serial import *

import os
import struct
import threading

class GpioTestWidget(QWidget):
    data_proc = pyqtSignal(int, bytes)
    def __init__(self, win, serial):
        super().__init__(None)
        self.main_win = win
        self.my_serial = serial
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+'/GpioTest.ui', self)

        self.btnRead.clicked.connect(self.onRead)
        self.btnWrite.clicked.connect(self.onWrite)
    
    def onRead(self):
        port = self.cbPort.currentIndex()
        pin = self.cbPin.currentIndex()
        state = self.my_serial.gpio_read_req(port, pin)
        self.edtState.setText(str(state))
        pass


    def onWrite(self):
        port = self.cbPort.currentIndex()
        pin = self.cbPin.currentIndex()
        state = int(self.edtState.text())
        self.my_serial.gpio_write_req(port, pin, state)
        pass