from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class Listener(QThread):
    isTouchSignal = pyqtSignal(str)

    def __init__(self, parent, listenerQueue):
        super().__init__(parent)
        self.parent = parent
        self.working = True
        self.listenerQueue = listenerQueue

    def run(self):
        while self.working:
            result = self.listenerQueue.get()
            self.isTouchSignal.emit(result) # "middle, 3"


class Window(QMainWindow):
    def __init__(self, handTrackingQueue, touchSensingQueue):
        super().__init__()
        self.title = "PyQt5 Drawing Tutorial"
        self.top= 150
        self.left= 150
        self.width = 500
        self.height = 500
        self.InitWindow()

        self.handTrackingResults = "1, 1"
        self.handTrackingListener = Listener(self, handTrackingQueue)
        self.handTrackingListener.isTouchSignal.connect(self.handTrackingHandler)
        self.handTrackingListener.start()

        self.touchSensingResults = True
        self.touchSensingListener = Listener(self, touchSensingQueue)
        self.touchSensingListener.isTouchSignal.connect(self.touchSensingHandler)
        self.touchSensingListener.start()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()
             
    def initListener(self, listenerQueue):
        self.listener = Listener(self, listenerQueue)
        self.listener.isTouchSignal.connect(self.handler)
        self.listener.start()


    @QtCore.pyqtSlot(str)
    def handTrackingHandler(self, result):
        results = result.split(",")
        self.handTrackingResults = (int(results[0]), int(results[1]))
        #self.handTrackingResults = result
        self.repaint()

    @QtCore.pyqtSlot(str)
    def touchSensingHandler(self, result):
        self.touchSensingResults = value
        #self.repaint()

    def paintEvent(self, event):
        if self.touchSensingResults:
            painter = QPainter(self)
            #painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))
            #painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            #painter.drawEllipse(40, 40, 400, 400)
            #painter.drawText(20, 40, self.handTrackingResults)
            painter.drawText(20, 40, str(self.handTrackingResults[0]) + ", " + str(self.handTrackingResults[1]))

            width = 30
            height = 20
            xPadding = 10
            yPadding = 15

            for finger in range(1, 5):
                for node in range(3):
                    if self.handTrackingResults[0] == finger and self.handTrackingResults[1] == node:
                        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
                    else:
                        painter.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
                    painter.drawRect((width + xPadding)*node, (height + yPadding) * finger, width, height)


