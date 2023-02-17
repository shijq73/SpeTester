import sys
import os

start_path = os.path.dirname(os.path.abspath(sys.argv[0])) 

sys.path.append(start_path + '\Python39')
sys.path.append(start_path + '\Python39\Lib\site-packages')
sys.path.append(start_path + '\Python39\dlls')
sys.path.append(start_path + '\Python39\libs')
sys.path.append(start_path + '\Python39\lib')
sys.path.append(start_path + '\.venv\Lib\site-packages')

import struct
import traceback
import glob
import configparser

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from my_serial import *

from GpioTest.GpioTest import GpioTestWidget
from adc_test.adc_test import AdcTestWidget
from dac_test.dac_test import DacTestWidget

class MyStdOut():
    def __init__(self, obj):
        self.obj = obj

    def write(self, txt):
        self.obj.update_gui.emit(UPDATE_LOG, [txt])


class DscEvalWin(QMainWindow):
    update_gui = pyqtSignal(int, list)
    def __init__(self, parent=None):
        super(DscEvalWin, self).__init__(parent)
        
        uic.loadUi(os.path.dirname(os.path.abspath(__file__))+'/main.ui', self)
        self.my_serial = MySerial()

        self.cbPort.popupAboutToBeShown.connect(self.populateCombo)
        self.btnConnect.clicked.connect(self.onConnect)
        self.btnDisconnect.clicked.connect(self.onDisconnect)

        self.tab_widgets = {}

        self.createWidgets()

        self.test_frame.setEnabled(False)

        self.update_gui.connect(self.onUpdateGUI)
        my_stdout = MyStdOut(self)
        my_stderr = MyStdOut(self)
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = my_stdout
        sys.stderr = my_stderr

    def createWidgets(self):
        self.wGpioTest = GpioTestWidget(self, self.my_serial)    
        self.wAdcTest = AdcTestWidget(self, self.my_serial)  
        self.wDacTest = DacTestWidget(self, self.my_serial)  

        self.tab_widgets['GPIO Testing'] = self.wGpioTest
        self.tab_widgets['ADC Testing'] = self.wAdcTest
        self.tab_widgets['DAC Testing'] = self.wDacTest

        for tab_index in range(self.twTest.count()):
            self.twTest.removeTab(0)

    def onUpdateGUI(self, target, obj):
        if target == UPDATE_LOG:
            self.edtLog.setUpdatesEnabled(False);
            prev_cursor = self.edtLog.textCursor();
            self.edtLog.moveCursor(QTextCursor.End)
            self.edtLog.insertPlainText(obj[0])
            self.edtLog.setTextCursor(prev_cursor)
            self.edtLog.setUpdatesEnabled(True)


    def serial_ports(self):
        """ Lists serial port names
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                #result.append(port)
            except OSError as error:
                if sys.platform.startswith('win'):
                    if("FileNotFoundError" in error.args[0]): continue
                    pass
                elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                    if len(error.args)<=1 or ("could not open port" in error.args[1]): continue
                    pass                
            result.append(port)
        return result

    def populateCombo(self):
        current_text = self.cbPort.currentText()
        self.cbPort.clear()
        for addr in self.serial_ports():
            self.cbPort.addItem(addr, addr)

        self.cbPort.setCurrentIndex(self.cbPort.findText(current_text, Qt.MatchFixedString))
        self.cbPort.setCurrentText(current_text)


    def onConnect(self):
        connected = False
        self.btnConnect.setEnabled(False)
        self.my_serial.close()
        try:
            self.edtLog.clear()
            self.my_serial.open(self.cbPort.currentText(),int(self.edtBaud.text()))

            node_info = self.my_serial.get_board_identity()
            if node_info == None: 
                return

            self.test_frame.setEnabled(True)

            self.twTest.addTab(self.wGpioTest, 'GPIO Testing')
            self.twTest.addTab(self.wAdcTest, 'ADC Testing')
            self.twTest.addTab(self.wDacTest, 'DAC Testing')

            connected = True
            self.btnDisconnect.setEnabled(True)
        except:
            print(traceback.format_exc())
        
        finally:           
            if not connected:
                self.btnConnect.setEnabled(True)
                self.my_serial.close()
            
    def onDisconnect(self):
        self.btnDisconnect.setEnabled(False)

        for key in self.tab_widgets:
            widget = self.tab_widgets[key]
            #print(key,' - ', widget)          
            if hasattr(widget, 'handleDisconnect'):
                widget.handleDisconnect()
                 
        for tab_index in range(self.twTest.count()):
                self.twTest.removeTab(0)

        self.edtLog.clear()
        self.my_serial.cancel_read()
        self.my_serial.close()

        self.test_frame.setEnabled(False)

        connected = False
        self.btnConnect.setEnabled(True)
  
import logging

def my_excepthook(exctype, value, tb):
    traceback.print_exception(exctype, value, tb)
    logging.error(''.join(traceback.format_exception(exctype, value, tb)))
    pass
    
def something():
    pass
    # error_dialog = QtWidgets.QErrorMessage()
    # error_dialog.showMessage('Oh no!')
    # print(traceback.format_exc())

if __name__ == '__main__':
    sys.__excepthook__ = sys.excepthook
    sys.excepthook = my_excepthook

    logging.basicConfig(
        format='%(asctime)s {%(threadName)-12.12s] {%(levelname)-5.5s %(message)s',
        handlers=[
            logging.FileHandler('dsc_eval.log'),
            #logging.StreamHandler()
        ],
        level=logging.INFO)

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

    '''
    label = QLabel("""
            <font color=red size=128>
               <b>Hello PyQt， The window will disappear after 5 seconds！</b>
            </font>""")
    # SplashScreen - Indicates that the window is a splash screen. This is the default type for .QSplashScreen
    # FramelessWindowHint - Creates a borderless window. The user cannot move or resize the borderless window through the window system.
    label.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
    label.show()
    '''


    app.setWindowIcon(QIcon('icons/pizza.icon'))
    wnd = DscEvalWin()
    wnd.show()
    sys.exit(app.exec_())

    sys.excepthook = sys.__excepthook__
