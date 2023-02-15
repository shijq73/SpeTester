from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from msg_def import *
from my_serial import *

import os
import struct
import threading

class DacTestWidget(QWidget):
    update_gui = pyqtSignal()
    data_proc = pyqtSignal(bytes, int)
    def __init__(self, win, serial):
        super().__init__(None)
        self.main_win = win
        self.my_serial = serial
        self.test_in_progress = False
        
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+'/dac_test.ui', self)
        self.btnStart.setEnabled(True)
        self.btnWrite.setEnabled(False)
        self.btnStop.setEnabled(False)
        self.btnStart.clicked.connect(self.onStart)
        self.btnWrite.clicked.connect(self.onWrite)
        self.btnStop.clicked.connect(self.onStop)
        self.edtDacVal.textChanged.connect(self.onValChanged)
        self.edtVoltage.textChanged.connect(self.onValChanged)

        #self.update_gui.connect(self.onUpdateGUI)
        self.data_proc.connect(self.onProcessStat)

    def handleDisconnect(self):
        self.test_in_progress = False
        self.btnStart.setEnabled(True)
        self.btnWrite.setEnabled(False)
        self.btnStop.setEnabled(False)

    def onValChanged(self, new_str):        
        if self.sender() == self.edtDacVal:
            dac_val = int(new_str)
            if dac_val>=0 and dac_val<=4096:
                voltage = dac_val*3.296/4096
                self.edtVoltage.blockSignals(True)
                self.edtVoltage.setText(f'{voltage:2.4f}')
                self.edtVoltage.blockSignals(False)
        if self.sender() == self.edtVoltage:
            voltage = float(new_str)
            if voltage>=0 and voltage<3.3:
                dac_val = int(voltage*4096/3.296)
                self.edtDacVal.blockSignals(True)
                self.edtDacVal.setText(str(dac_val))
                self.edtDacVal.blockSignals(False)

    def onStart(self):
        #self.btnWrite.setEnabled(False)
        self.my_serial.dac_req(1, 0)
        if not self.test_in_progress:
            self.test_in_progress = True
            thrd = threading.Thread(target=self.process_thrd, args=())
            thrd.start()

    def onWrite(self):
        self.btnWrite.setEnabled(False)
        dac_val = int(self.edtDacVal.text())      
        self.my_serial.dac_req(2, dac_val)


    def onStop(self):
        self.btnStop.setEnabled(False)
        status = self.my_serial.dac_req(0, 0)
        if status == 0:
            self.btnStart.setEnabled(True)

    def process_thrd(self):
        more_data = 0
        while self.test_in_progress:
            msg_data = self.my_serial.get_msg_data()
            if msg_data == None: continue

            msg_id = msg_data[1]
            remote = msg_data[1] & 0x80==0x80
            msg_id &= ~0x80

            data = msg_data[2:]

            self.data_proc.emit(data, msg_id)

        #self.onThrdExit()

    def onProcessStat(self, data, msg_id):
        
        if msg_id == PERF_MSG.DAC_REQ | REQ_CONFIRM_MASK:
            self.onDacReqConfirm(data)
        #elif msg_id == PERF_MSG.ADC_REQ | IND_MASK:
        #    self.onAdcInd(data)

    def onDacReqConfirm(self, data):
        if data[0] == 0:

            if data[1] == 0:
                self.btnStart.setEnabled(True)
                self.btnWrite.setEnabled(False)
                self.btnStop.setEnabled(False)
                self.test_in_progress = False
            elif data[1] == 1:
                self.btnStart.setEnabled(False)
                self.btnWrite.setEnabled(True)
                self.btnStop.setEnabled(True)
                self.test_in_progress = True                
            if data[1] == 2:
                self.btnStart.setEnabled(False)
                self.btnWrite.setEnabled(True)
                self.btnStop.setEnabled(True)
                self.test_in_progress = True
            else:
                print('Unknown state')
        else:
            print('data[0] != 0')
            self.main_win.print_err(data[0])
            self.main_win.print_err(data)
            self.btnWrite.setEnabled(True)
            self.btnStop.setEnabled(False)
            self.test_in_progress = False       
