from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class Listener(QThread):
    isTouchSignal = pyqtSignal(int)

    def __init__(self, parent, listenerQueue):
        super().__init__(parent)
        self.parent = parent
        self.working = True
        self.listenerQueue = listenerQueue

    def run(self):
        while self.working:
            result = self.listenerQueue.get()
            self.isTouchSignal.emit(result[1])


class Window(QMainWindow):
    def __init__(self, listenerQueue):
        super().__init__()
        self.title = "PyQt5 Drawing Tutorial"
        self.top= 150
        self.left= 150
        self.width = 500
        self.height = 500
        self.InitWindow()

        #For event handling
        self.event = {"isTouch": False}
        self.initListener(listenerQueue)

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

             
    def initListener(self, listenerQueue):
        self.listener = Listener(self, listenerQueue)
        self.listener.isTouchSignal.connect(self.handler)
        self.listener.start()


    @QtCore.pyqtSlot(int)
    def handler(self, value):
        self.event["isTouch"] = value
        self.repaint()


    def paintEvent(self, event):
        if self.event["isTouch"]:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            painter.drawEllipse(40, 40, 400, 400)