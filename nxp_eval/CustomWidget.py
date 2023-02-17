from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic


class ComboBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()

class NodeWidget(QFrame):
    clicked = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.band = ''
        self.mcu_trx_name = ''
        self.board_name = ''
        self.board_id = ''
        self.title = ''
        self._status = ''
        self.show_band = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.focused = False
        self._selected = False
        self._node_info = None
        self.start_freq = 0
        self.stop_freq = 0
        self.step_freq = 0

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def node_info(self):
        return self._node_info

    @node_info.setter
    def node_info(self, value):
        self._node_info = value

        #self.board_name = self._node_info.board_name
        #self.board_id = self._node_info.board_id
        #self.mcu_trx_name = self._node_info.mcu_name + '/' + self._node_info.trx_name

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self.update()

    '''
    def focusInEvent(self, event):
        #print(self.title + ' -- focusInEvent')
        self.focused = True
        self.selected = True
        self.update()

    def focusOutEvent(self, event):
        #print(self.title + ' -- focusOutEvent')
        self.focused = False
        self.update()

    '''
    def clearLayout(self):
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def mousePressEvent(self, event):
        #print('mousePressEvent')
        # self.clicked.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        #print ("test 2")
        super().mousePressEvent( event)

    def paintEvent(self, event):
        qp = QPainter(self)
        self.board_name = self._node_info.board_name
        self.board_id = self._node_info.board_id
        self.mcu_trx_name = self._node_info.mcu_name + '/' + self._node_info.trx_name
        self.dwawBorder(qp)
        self.drawTitle(qp)

    def drawTitle(self, painter):
        width = self.size().width()-30
        height = self.size().height()-1
        font = QFont("Arial", 12, 0, False)

        font.setBold(True)
        font.setUnderline(self.selected)

        painter.setFont(font)

        if self.focused:
            pen = QPen(QColor(46, 107, 199, 255))
        else:
            if self.selected:
                pen = QPen(QColor(100, 100, 100, 255))
            else:
                pen = QPen(QColor(0, 0, 0, 255))

        painter.setPen(pen)

        painter.drawText(QRectF(6,6,width,23), Qt.AlignCenter|Qt.AlignTop, self.title)

        font = QFont("Arial", 9, 0, False)
        font.setBold(False)
        painter.setFont(font)
        pen = QPen(QColor(0, 0, 0, 255))
        painter.setPen(pen)

        painter.drawText(QRectF(6, 30, width, 18), Qt.AlignCenter | Qt.AlignTop, self.mcu_trx_name)

        if self.show_band:
            painter.drawText(QRectF(6, 30+18, width, 20), Qt.AlignCenter | Qt.AlignTop, self.band)
        else:
            painter.drawText(QRectF(6, 30 + 18, width, 20), Qt.AlignCenter | Qt.AlignTop, '')

        painter.drawText(QRectF(6, 30+18*2, width, 20), Qt.AlignCenter | Qt.AlignTop, self.board_name)
        painter.drawText(QRectF(6, 30+18*3, width, 20), Qt.AlignCenter | Qt.AlignTop, self.board_id.hex())

        pen =  QPen(QColor(50, 100, 50, 255))
        painter.setPen(pen)

        font = QFont("Arial", 11, 0, False)
        font.setBold(False)
        painter.setFont(font)

        painter.translate(self.size().width()-15, self.size().height()-12)
        painter.rotate(-90)
        painter.drawText(0,0,self._status)

    def dwawBorder(self, painter):
        brush = QBrush(QColor(255, 255, 255, 255))
        pen = QPen(QColor(0, 0, 0, 255))

        if self.selected:
            pen_width = 2
            pen = QPen(QColor(46, 107, 199, 255))
        else:
            pen_width = 1
            pen = QPen(QColor(0, 0, 0, 255))

        pen.setWidth(pen_width)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawRect(pen_width, pen_width, self.size().width() - 2*pen_width, self.size().height() - 2*pen_width)

        pen = QPen(QColor(146, 173, 86, 255))
        pen.setWidth(3)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawLine(
            6,
            6,
            self.size().width() - 6,
            6
        )

        painter.drawLine(
            self.size().width() - 6,
            6,
            self.size().width() - 6,
            self.size().height() - 6,
        )


        pen.setWidth(1)
        painter.setPen(pen)

        brush = QBrush(QColor(255, 243, 214, 255))
        painter.setBrush(brush)

        painter.drawLine(
            6,
            30,
            self.size().width() - 30,
            30
        )


        painter.drawRect(
            self.size().width() - 30,
            7,
            30-7,
            self.size().height() - 12)

    def paintEvent11(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mouseReleaseEvent(self, event):
        #print('mouseReleaseEvent')
        self.clicked.emit()
        super().mouseReleaseEvent(event)