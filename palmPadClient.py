from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QBrush, QPen, QCursor
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
            print("listener: " , result)
            self.isTouchSignal.emit(result) # "middle, 3"


class Window(QMainWindow):
    def __init__(self, handTrackingQueue):
        super().__init__()
        self.title = "PyQt5 Drawing Tutorial"
        self.top= 150
        self.left= 150
        self.width = 500
        self.height = 500
        self.InitWindow()

        self.cursor = QCursor(Qt.ClosedHandCursor)
        self.setCursor(self.cursor)

        self.handTrackingResults = (0, 0)
        self.handTrackingListener = Listener(self, handTrackingQueue)
        self.handTrackingListener.isTouchSignal.connect(self.handTrackingHandler)
        self.handTrackingListener.start()

        self.mouseX = 600
        self.mouseY = 600

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
        if touchSensingResults:
            results = result.split(",")
            if results[0] == "0": #PalmPad
                self.handTrackingResults = (float(results[1]), float(results[2]))
            
                dx, dy = self.handTrackingResults    
                self.mouseX -= dx
                self.mouseY += dy
                self.cursor.setPos(self.mouseX, self.mouseY)
                print(dx, dy)

    # @QtCore.pyqtSlot(str)
    # def touchSensingHandler(self, result):
    #     self.touchSensingResults = bool(int(result))
    #     #dx, dy = self.handTrackingResults
    #     #self.mouseX += dx
    #     #self.mouseY += dy
    #     #self.cursor.setPos(self.mouseX, self.mouseY)
        
        

    def paintEvent(self, event):
        pass
        #if self.touchSensingResults:
            #painter = QPainter(self)
            #painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))
            #painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            #painter.drawEllipse(40, 40, 400, 400)
            #painter.drawText(20, 40, self.handTrackingResults)


