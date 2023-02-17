from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from msg_def import *
from my_serial import *

import os
import struct
import threading


class DifferentialPairWidget(QFrame):

    update_gui = pyqtSignal()

    def __init__(self, win, name1, name2):
        super().__init__(None)
        self.win = win
        layout = QHBoxLayout()
        layout.setContentsMargins(3,3,3,3)
        self.setLayout(layout)
        
        self.differential_frame = QFrame()
        layout.addWidget(self.differential_frame)

        self.frame_layout = QHBoxLayout()
        self.frame_layout.setContentsMargins(3,3,3,3)

        self.differential_frame.setLayout(self.frame_layout)
        self.differential_frame.setFrameShape(QFrame.Shape.Box)
        self.differential_frame.setFrameShadow(QFrame.Shadow.Plain)


        self.label1 = QLabel(name1)
        self.frame_layout.addWidget(self.label1)

        self.seperator = QLabel('')
        self.frame_layout.addWidget(self.seperator)
        self.seperator.setFrameShape(QFrame.Shape.VLine)
        self.seperator.setFrameShadow(QFrame.Shadow.Plain)

        self.label2 = QLabel(name2)
        self.frame_layout.addWidget(self.label2)

        self.check_box = QCheckBox('Differential')
        layout.addWidget(self.check_box)

        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.check_box.clicked.connect(self.onCheck)

        self.onCheck()

    def onCheck(self):
        if self.check_box.isChecked():
            self.frame_layout.setContentsMargins(3,3,3,3)
            self.differential_frame.setFrameShape(QFrame.Shape.Box)
            self.differential_frame.setFrameShadow(QFrame.Shadow.Plain)
            self.seperator.setFrameShape(QFrame.Shape.VLine)
            self.seperator.setFrameShadow(QFrame.Shadow.Plain)
        else:
            self.frame_layout.setContentsMargins(4,5,4,5)
            self.differential_frame.setFrameShape(QFrame.Shape.NoFrame)
            self.differential_frame.setFrameShadow(QFrame.Shadow.Plain)
            self.seperator.setFrameShape(QFrame.Shape.NoFrame)
            self.seperator.setFrameShadow(QFrame.Shadow.Plain)

        
        self.win.update_gui.emit()

    def isDifferential(self):
        return self.check_box.isChecked()


class AdcTestWidget(QWidget):
    update_gui = pyqtSignal()
    data_proc = pyqtSignal(bytes, int)
    def __init__(self, win, serial):
        super().__init__(None)
        self.main_win = win
        self.my_serial = serial

        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+'/adc_test.ui', self)
        #self.btnStart.setEnabled(True)
        #self.btnStop.setEnabled(False)

        self.init_input_config()
        self.init_scan_config() 
        self.initScanModeComboBox()

        self.btnStart.clicked.connect(self.onStart)
        self.btnStop.clicked.connect(self.onStop)
        self.update_gui.connect(self.onUpdateGUI)
        self.data_proc.connect(self.onProcessStat)

    def initScanModeComboBox(self):
        combobox = self.cbScanMode
        combobox.clear()
        combobox.addItem('Once (single) sequential',0)
        combobox.addItem('Once parallel independently',1)
        combobox.addItem('Loop sequential',2)
        combobox.addItem('Loop parallel independently',3)
        combobox.addItem('Triggered sequential',4)
        combobox.addItem('Triggered parallel independently',5)
        combobox.addItem('Once parallel simultaneously', 1<<4)
        combobox.addItem('oop parallel simultaneously',3<<4)
        combobox.addItem('Triggered parallel simultaneously',5<<4)        
        combobox.adjustSize()         

    def handleDisconnect(self):
        self.test_in_progress = False
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)       


    def init_input_config(self):
        an_in_layout = self.gpAnalogInputConfig.layout()
        self.clearLayout(an_in_layout)

        row1_layout = QHBoxLayout()
        an_in_layout.addLayout(row1_layout)

        self.pair_list = []
        for i in range(4):
            pair = DifferentialPairWidget(self,'ANA'+str(i*2), 'ANA'+str(i*2+1))
            self.pair_list.append(pair)
            row1_layout.addWidget(pair)
            #print(pair.parent())

        row2_layout = QHBoxLayout()
        an_in_layout.addLayout(row2_layout)

        for i in range(4):
            pair = DifferentialPairWidget(self,'ANB'+str(i*2), 'ANB'+str(i*2+1))
            self.pair_list.append(pair)
            row2_layout.addWidget(pair)   

    def init_scan_config(self):

        self.slot_checkboxs = []
        self.slot_comboboxes= []
        self.slot_lineedit= []

        scan_slot_layout = self.gpScanSlot.layout()
        self.clearLayout(scan_slot_layout)

        for row in range(5):
            row_layout =  QHBoxLayout()
            scan_slot_layout.addLayout(row_layout)

            for col in range(4):
                col_layout = QHBoxLayout()
                row_layout.addLayout(col_layout)      

                #check_box = QCheckBox(str(row*4+col).zfill(2))
                #col_layout.addWidget(check_box)
                #self.slot_checkboxs.append(check_box)
                label = QLabel(str(row*4+col).zfill(2))
                col_layout.addWidget(label)
                self.slot_checkboxs.append(label)

                combobox = QComboBox()
                #combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                combobox.setFixedWidth(120)
                col_layout.addWidget(combobox)
                self.slot_comboboxes.append(combobox)

                edit_box = QLineEdit()
                #edit_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                #edit_box.setFixedWidth(50)
                col_layout.addWidget(edit_box)                          
                self.slot_lineedit.append(edit_box)    
    
        self.onUpdateGUI()

        for index in range(16,20):
            combobox = self.slot_comboboxes[index]
            combobox.clear()
            combobox.addItem('ADCATemperature',16)
            combobox.addItem('ADCAOnchipInput',17)
            combobox.addItem('ADCBTemperature',18)
            combobox.addItem('ADCBOnchipInput',19)           
            combobox.adjustSize()  

    def onUpdateGUI(self):
        list1,list2 = self.getInputList()
        for index in range(16):
            combobox = self.slot_comboboxes[index]
            current_index = combobox.currentIndex()
            current_text = combobox.currentText()
            current_data = combobox.currentData()            
            combobox.clear()
            for item_index in range(len(list2)):
                combobox.addItem(list2[item_index],list1[item_index])
            new_data = combobox.itemData(current_index)
            if current_text in list2:
                combobox.setCurrentText(current_text)
            elif current_data and current_data&0x7f==new_data&0x7f:
                combobox.setCurrentIndex(current_data&0x7f)
            elif current_data and \
                 current_index and \
                 current_index<combobox.count() and \
                 new_data==current_data+1:
                combobox.setCurrentIndex(current_index-1)

            combobox.adjustSize()          

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
    
    def getInputList(self):
        analog_input_list = []
        input_str_list = []
        index = 0
        for pair in self.pair_list:
            if pair.isDifferential():
                analog_input_list.append(0x80|index*2) 
                if index < 4:
                    input_str_list.append('DiffANA{0}pANA{1}n'.format(index*2,index*2+1))
                else:
                    input_str_list.append('DiffANB{0}pANB{1}n'.format(index*2-8,index*2-7))
            else:
                analog_input_list.append(index*2)
                analog_input_list.append(index*2+1)

                if index < 4:
                    input_str_list.append('SingleEndANA{0}'.format(index*2))
                    input_str_list.append('SingleEndANA{0}'.format(index*2+1))
                else:
                    input_str_list.append('SingleEndANB{0}'.format(index*2-8))
                    input_str_list.append('SingleEndANB{0}'.format(index*2-7))
            index += 1

        return analog_input_list,input_str_list


    def onStart(self):
        self.btnStart.setEnabled(False)
        scan_mode = self.cbScanMode.currentData()
        dma_en = 0
        scan_list = [0]*20
        for index in range(len(self.slot_comboboxes)):
            #if self.slot_checkboxs[index].isChecked():
            combobox = self.slot_comboboxes[index]
            scan_list[index] = combobox.currentData()
            #else:
            #    scan_list[index] = combobox.currentData()
       
        self.my_serial.adc_req(1, scan_mode, dma_en, scan_list)

        self.test_in_progress = True
        thrd = threading.Thread(target=self.process_thrd, args=())
        thrd.start()

    def onStop(self):
        self.btnStop.setEnabled(False)
        status = self.my_serial.adc_req(0, 0, 0, 0)
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
        
        if msg_id == PERF_MSG.ADC_REQ | REQ_CONFIRM_MASK:
            self.onAdcReqConfirm(data)
        elif msg_id == PERF_MSG.ADC_REQ | IND_MASK:
            self.onAdcInd(data)

    def onAdcReqConfirm(self, data):
        if data[0] == 0:
            if data[1] == 1:
                self.btnStart.setEnabled(False)
                self.btnStop.setEnabled(True)
                self.test_in_progress = True
            elif data[1] == 0:
                self.btnStart.setEnabled(True)
                self.btnStop.setEnabled(False)
                self.test_in_progress = False
            else:
                print('Unknown state')
        else:
            print('data[0] != 0')
            self.main_win.print_err(data[0])
            self.main_win.print_err(data)
            self.btnStart.setEnabled(True)
            self.btnStop.setEnabled(False)
            self.test_in_progress = False       

    def onAdcInd(self, data):
        print('onAdcInd')
        status = data[0]
        voltage_list = [0.0]*20
        volt_data_list = struct.unpack("=20h",data[1:])
        index = 0
        for index in range(20):
            if self.slot_comboboxes[index].currentData() > 0x80:
                voltage_list[index] = 3.28*((volt_data_list[index]>>3)-2048)/2048
            else:
                voltage_list[index] = 3.28*(volt_data_list[index]>>3)/4096
            self.slot_lineedit[index].setText('% 2.4f' % voltage_list[index])
            index += 1
