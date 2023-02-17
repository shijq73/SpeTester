from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from msg_def import *
from my_serial import *

import os
import struct
import threading

gpio1_pin_list = [
    '(Pin 13) GPIO_00',
    '(Pin 12) GPIO_01',
    '(Pin 11) GPIO_02',
    '(Pin 09) GPIO_03',
    '(Pin 08) GPIO_04',
    '(Pin 07) GPIO_05',
    '(Pin 06) GPIO_06',
    '(Pin 05) GPIO_07',
    '(Pin 04) GPIO_08',
    '(Pin 03) GPIO_09',
    '(Pin 02) GPIO_10',
    '(Pin 01) GPIO_11',
    '(Pin 80) GPIO_12',
    '(Pin 79) GPIO_13',
    '(Pin 60) GPIO_AD00',
    '(Pin 59) GPIO_AD01',
    '(Pin 58) GPIO_AD02',
    '(Pin 57) GPIO_AD03',
    '(Pin 56) GPIO_AD04',
    '(Pin 55) GPIO_AD05',
    '(Pin 52) GPIO_AD06',
    '(Pin 51) GPIO_AD07',
    '(Pin 49) GPIO_AD08',      
    '(Pin 48) GPIO_AD09',
    '(Pin 47) GPIO_AD10',
    '(Pin 46) GPIO_AD11', 
    '(Pin 45) GPIO_AD12',
    '(Pin 44) GPIO_AD13',
    '(Pin 43) GPIO_AD14', 
    ]

gpio2_pin_list = [
    '(Pin 76) GPIO_SD00',
    '(Pin 75) GPIO_SD01',
    '(Pin 74) GPIO_SD02',
    '(Pin 73) GPIO_SD03',
    '(Pin 72) GPIO_SD04',
    '(Pin 70) GPIO_SD05',
    '(Pin 69) GPIO_SD06',
    '(Pin 68) GPIO_SD07',
    '(Pin 67) GPIO_SD08',
    '(Pin 66) GPIO_SD09',
    '(Pin 65) GPIO_SD10',
    '(Pin 64) GPIO_SD11',
    '(Pin 62) GPIO_SD12',
    '(Pin 61) GPIO_SD13',    
    ]

#gpio5_pin_list = [
#    '(Pin 24) PMIC_ON_REQ', 
#    ]

PERPHERAL_GPIO1 = 0
PERPHERAL_GPIO2 = 1
PERPHERAL_GPIO5 = 2

class GpioTestWidget(QWidget):

    update_gui = pyqtSignal()
    data_proc = pyqtSignal(bytes, int)

    def __init__(self, win, serial):
        super().__init__(None)
        self.main_win = win
        self.my_serial = serial
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+'/GpioTest.ui', self)

        self.initPinList()

        self.btnRead.clicked.connect(self.onRead)
        self.btnWrite.clicked.connect(self.onWrite)
        self.rbGpio1.toggled.connect(self.initPinList)
        self.rbGpio2.toggled.connect(self.initPinList)        
        #self.rbGpio5.toggled.connect(self.initPinList)

        self.update_gui.connect(self.onUpdateGUI)
        self.data_proc.connect(self.onProcessStat)

    def initPinList(self):
        last_index = self.cbPin.currentIndex()

        self.cbPin.clear()

        if self.rbGpio1.isChecked():
            self.cbPin.addItems(gpio1_pin_list)
        if self.rbGpio2.isChecked():
            self.cbPin.addItems(gpio1_pin_list)
            self.cbPin.addItems(gpio2_pin_list)

        if last_index < self.cbPin.count():
            self.cbPin.setCurrentIndex(last_index)
        else:
            self.cbPin.setCurrentIndex(0)
        #if self.rbGpio5.isChecked():
        #    self.cbPin.addItems(gpio5_pin_list)


    def onRead(self):

        #self.btnRead.setEnabled(False)
        peripheral = 0
        if self.rbGpio1.isChecked():
            peripheral = PERPHERAL_GPIO1
        if self.rbGpio2.isChecked():
            peripheral = PERPHERAL_GPIO2
        #if self.rbGpio5.isChecked():
        #    peripheral = PERPHERAL_GPIO5

        pin = self.cbPin.currentIndex()

        #self.test_in_progress = False

        if 'Start' in self.btnRead.text():
            self.my_serial.gpio_read_req(peripheral, pin, 1)
            #self.edtState.setText(str(state))

            #print("onRead")
            
            self.test_in_progress = True
            thrd = threading.Thread(target=self.process_thrd, args=())
            thrd.start()
        else:
            self.my_serial.gpio_read_req(peripheral, pin, 0)

    def onWrite(self):
        peripheral = 0
        if self.rbGpio1.isChecked():
            peripheral = PERPHERAL_GPIO1
        if self.rbGpio2.isChecked():
            peripheral = PERPHERAL_GPIO2
        pin = self.cbPin.currentIndex()
        state = int(self.edtState.text())
        self.my_serial.gpio_write_req(peripheral, pin, state)
        pass

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

        self.onThrdExit()

    def onThrdExit(self):
        print('onThrdExit')


    def onProcessStat(self, data, msg_id):
        
        if msg_id == PERF_MSG.GPIO_READ_REQ | REQ_CONFIRM_MASK:
            self.onGpioReqConfirm(data)
        elif msg_id == PERF_MSG.GPIO_READ_REQ | IND_MASK:
            self.onGpioReadReqInd(data)

    def onGpioReqConfirm(self, data):
        if data[0] == 0:
            if data[1] == 1:
                self.btnRead.setEnabled(True)
                self.btnRead.setText('Read (Stop)')
                #self.btnStop.setEnabled(True)
                self.test_in_progress = True
            elif data[1] == 0:
                self.btnRead.setEnabled(True)
                self.btnRead.setText('Read (Start)')
                #self.btnStop.setEnabled(False)
                self.test_in_progress = False

    def onGpioReadReqInd(self, data):
        if data[0] == 0:
            port_index = data[1]
            pin = data[2]
            pin_index = self.cbPin.currentIndex()

            if pin_index>=29:
                pin_index -= 29

            if data[3]:
                print('Button Released')
            else:
                print('Button Pressed')  

            if pin_index == pin and \
               (self.rbGpio1.isChecked() and port_index == 0 or \
                self.rbGpio2.isChecked() and port_index == 1):
                self.edtState.setText(str(data[3]))

    def onUpdateGUI(self):
        pass