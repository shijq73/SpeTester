import serial
import traceback
import struct
from msg_def import *

from PyQt5.QtCore import pyqtSignal, QThread

UPDATE_LOG = 0
MSG_RECEIVED = 1

SOT = 1
EOT = 4

def debug_print(*args, **kwargs):
    print(*args, **kwargs)
    QApplication.processEvents() #update gui for pyqt

class NodeInfo:
    def __init__(self, count):
        self.count = count
        self.band  = 0
        self.freq = 0
        self.power = 0
        self.board_type = 0
        self.freq_offset = 0
        self.board_name = ''
        self.trx_name = ''
        self.mcu_name = ''
        self.curves = [None] * count
        self.data_count = 0

        self.curve_data = [] #[CurveInfo()] * count

        #for i in range(count):
        #    self.curve_data.append(CurveInfo())

        self.selected_curve = None
        self.board_id = None
        self.fw_ver = [0,0,0,0]
        self.tmp_ver = 0

    @property
    def fw_ver_f(self):
        return self.get_fw_ver_float(self.fw_ver)

    def get_fw_ver_float(self, fw_ver):
        fw_ver_str = '{0}.{1}{2}{3}'.format(fw_ver[0],fw_ver[1],fw_ver[2],fw_ver[3])
        return float(fw_ver_str)

class MySerial:
    UART_RX_STATE_SOT = 1
    UART_RX_STATE_LENGTH = 2
    UART_RX_STATE_DATA = 3
    UART_RX_STATE_EOT = 4

    def __init__(self):
        self.ser = None


    def __del__(self):     
        pass   

    def open(self, port, baudrate):
        self.close() 
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.1)
        self.rx_state = MySerial.UART_RX_STATE_SOT
        self.stopFlag = False  

    def close(self):
         if(self.ser != None):
            self.ser.close()
            self.ser = None        

    def sendMsg(self,protocol, msg_id, msg, remote=False):
        #self.current_msg_list.append([protocol, msg_id, msg, remote])
        #if len(self.current_msg_list) == 1:            
        self.__sendMsg(protocol, msg_id, msg, remote)
        #else:
        #    self.current_msg_list.append([protocol, msg_id, msg, remote])

    # ----------------------------------------------------------------------------------------
    # |  SOT    |   Msg_Length  | Protocol_ld   |  Msg_Id  |      Msg_Payload      |  EOT    |
    # ----------------------------------------------------------------------------------------
    # |(1 byte) |     (1 byte)  |   (1 byte)    | (1 byte) |(Msg Length –2) bytes  |(1 byte) |
    # ----------------------------------------------------------------------------------------
    def __sendMsg(self,protocol, msg_id, msg, remote=False):
        #print('__sendMsg')
        msg_len = 2 if msg == None else (len(msg)+2)

        if msg_id not in [
            PERF_MSG.IDENTIFY_BOARD_REQ,
        ]:

            if remote:
                msg_id |= 0x80

        frame = struct.pack('BBBB',SOT,msg_len,protocol,msg_id)

        if msg != None:
            frame += msg
        frame += b'\x04' # EOT

        #print(frame)
        self.ser.write(frame)

    def cancel_read(self):
        if self.ser != None:
            self.ser.cancel_read()

    def __recv(self):
        try:
            msg_data = bytes()
            ch = self.ser.read(1)

            if len(ch) == 0: return None
            #print(ch)
            if ord(ch) != MySerial.UART_RX_STATE_SOT: 
                return None

            ch = self.ser.read(1)
            if len(ch) == 0: return None

            rx_length = ord(ch)
            
            msg_data = self.ser.read(rx_length)
            if len(msg_data) == 0: return None

            ch = self.ser.read(1)
            if len(ch) == 0: return None

            if ord(ch) != MySerial.UART_RX_STATE_EOT: 
                return None

            return msg_data
        except:
            return None

    def get_msg_data(self):
        msg_data = self.__recv()
        return msg_data

    def get_fw_ver(self, data):
        # first check if is a old version
        fw_ver, = struct.unpack('I', data)

        if fw_ver == 0x404CCCCD:
            print('Old version')
            return [0,0,0,0]
        else:
            fw_ver, = struct.unpack('f', data)
            if fw_ver == 1.0 or fw_ver == 1065353216.0:
                print('1.0 old version')
                return [0,0,0,0]
            else:
                print(str(data[0])+'.'+ str(data[1])+'.'+ str(data[2])+'.'+ str(data[3]))
                return data
                
    def get_board_identity(self):
        self.sendMsg(0x0, PERF_MSG.IDENTIFY_BOARD_REQ, b'\xAA')
        msg_data = self.__recv()
        if msg_data == None: return None

        msg_id = msg_data[1]
        remote = msg_data[1] & 0x80==0x80
        msg_id &= ~0x80

        data = msg_data[2:]

        index = 0
        node_info = NodeInfo(5)
        status, band, mcu_name_len, = struct.unpack('BBB', data[index:index + 3])
        node_info.band = band       
   
        if status != 0x00: return None
        index += 3

        node_info.mcu_name = data[index:mcu_name_len + index].decode()

        index += mcu_name_len

        transceiver_name_len, = struct.unpack('B', data[index:index + 1])
        index += 1

        node_info.trx_name = data[index:transceiver_name_len + index].decode()
        index += transceiver_name_len

        board_name_len, = struct.unpack('B', data[index:index + 1])
        index += 1

        try:
            node_info.board_name = data[index:board_name_len + index].decode()
        except:
            node_info.board_name = 'no_name'
        
    
        index += board_name_len

        return node_info

    def gpio_read_req(self, port, pin, start_stop):
        msg_data = struct.pack('=BBB', port, pin, start_stop)
        self.sendMsg(0x0, PERF_MSG.GPIO_READ_REQ, msg_data, 0)

        return
        msg_data = self.__recv()
        if msg_data == None: return None
             
        msg_id = msg_data[1]
        remote = msg_data[1] & 0x80==0x80
        msg_id &= ~0x80

        data = msg_data[2:]
        status, state, = struct.unpack('BB', data[0:2])

        if status != 0x00: return None
        
        return state

    def gpio_write_req(self, port, pin, state):
        msg_data = struct.pack('=BBB', port, pin, state)
        self.sendMsg(0x0, PERF_MSG.GPIO_WRITE_REQ, msg_data, 0)

    # ----------------------------------------------------
    # | start_stop | scan_modem | dma_en | scan_list[20] |
    # ----------------------------------------------------
    def adc_req(self, start_stop, scan_modem, dma_en, scan_list):
        if start_stop:
            msg_data = struct.pack('=BBB20B', start_stop, scan_modem, dma_en, *scan_list)
        else:
            msg_data = struct.pack('=B', start_stop)
        self.sendMsg(0x0, PERF_MSG.ADC_REQ, msg_data, 0)        

    # ----------------------------------
    # | start_stop | dac_val(uint16_t) |
    # ----------------------------------
    def dac_req(self, start_stop, dac_val):
        if start_stop:
            msg_data = struct.pack('=BH', start_stop, dac_val)
        else:
            msg_data = struct.pack('=B', start_stop)
        self.sendMsg(0x0, PERF_MSG.DAC_REQ, msg_data, 0)   

class TSerialThrd(QThread):
    UART_RX_STATE_SOT = 1
    UART_RX_STATE_LENGTH = 2
    UART_RX_STATE_DATA = 3
    UART_RX_STATE_EOT = 4

    update_gui = pyqtSignal(int, list)

    def __init__(self, parent, serial):
        super(TSerialThrd, self).__init__()
        self.R30Wnd = parent
        self.ser = serial
        self.rx_state = TSerialThrd.UART_RX_STATE_SOT
        self.stopFlag = False

    def stop(self):
        self.stopFlag = True

    def handle_incoming_msg(self, data):
        self.update_gui.emit(MSG_RECEIVED, [data])

    def run(self):
        msg_data = bytes()
        rx_length = 0
        while not self.stopFlag:
            try:
                ch = self.ser.read(1)
                #print('{:02x} '.format(ch[0]), end='')
                if ch == b'':
                    break

                if self.rx_state == TSerialThrd.UART_RX_STATE_SOT:
                    if ord(ch) == SOT:
                        msg_data = bytes()
                        self.rx_state = TSerialThrd.UART_RX_STATE_LENGTH
                    else:
                        self.msleep(10)
                elif self.rx_state == TSerialThrd.UART_RX_STATE_LENGTH:
                    rx_length = ord(ch)
                    if rx_length:
                        self.rx_state = TSerialThrd.UART_RX_STATE_DATA
                    else:
                        self.rx_state = TSerialThrd.UART_RX_STATE_SOT;
                elif self.rx_state == TSerialThrd.UART_RX_STATE_DATA:
                    msg_data += ch
                    rx_length -= 1
                    if rx_length == 0:
                        self.rx_state = TSerialThrd.UART_RX_STATE_EOT
                elif self.rx_state == TSerialThrd.UART_RX_STATE_EOT:
                    if EOT == ord(ch):
                        self.handle_incoming_msg(msg_data)
                    else:
                        print('Unexpected data')
                    # print('\r\n')
                    self.rx_state = TSerialThrd.UART_RX_STATE_SOT
                else:
                    sio_rx_state = TSerialThrd.UART_RX_STATE_SOT;
            except Exception as e:
                traceback.print_exc()
                #print(e.)
                break
