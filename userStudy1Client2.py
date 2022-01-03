from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
import tkinter as tk
import random
from multiprocessing import Process, Queue

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

# 
# class Window(QMainWindow):
#     def __init__(self, handTrackingQueue):
#         super().__init__()
#         self.title = "PyQt5 Drawing Tutorial"
#         self.top= 150
#         self.left= 150
#         self.width = 500
#         self.height = 500
#         self.InitWindow()

#         self.cursor = QCursor(Qt.ClosedHandCursor)
#         self.setCursor(self.cursor)

#         self.handTrackingResults = (0, 0)
#         self.handTrackingListener = Listener(self, handTrackingQueue)
#         self.handTrackingListener.isTouchSignal.connect(self.handTrackingHandler)
#         self.handTrackingListener.start()

#         self.mouseX = 600
#         self.mouseY = 600

#     def InitWindow(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.top, self.left, self.width, self.height)
#         self.show()
             
#     def initListener(self, listenerQueue):
#         self.listener = Listener(self, listenerQueue)
#         self.listener.isTouchSignal.connect(self.handler)
#         self.listener.start()


#     @pyqtSlot(str)
#     def handTrackingHandler(self, result):
#         if touchSensingResults:
#             results = result.split(",")
#             if results[0] == "0": #PalmPad
#                 self.handTrackingResults = (float(results[1]), float(results[2]))
            
#                 dx, dy = self.handTrackingResults    
#                 self.mouseX -= dx
#                 self.mouseY += dy
#                 self.cursor.setPos(self.mouseX, self.mouseY)
#                 # print("dxy: ", dx, dy)

#     # @pyqtSlot(str)
#     # def touchSensingHandler(self, result):
#     #     self.touchSensingResults = bool(int(result))
#     #     #dx, dy = self.handTrackingResults
#     #     #self.mouseX += dx
#     #     #self.mouseY += dy
#     #     #self.cursor.setPos(self.mouseX, self.mouseY)
        
        

#     def paintEvent(self, event):
#         pass
#         #if self.touchSensingResults:
#             #painter = QPainter(self)
#             #painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))
#             #painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
#             #painter.drawEllipse(40, 40, 400, 400)
#             #painter.drawText(20, 40, self.handTrackingResults)


class MouseClickButton(QPushButton):
    def __init__(self, parent=None):
        super(MouseClickButton, self).__init__(parent)
        self.setStyleSheet("background-color : yellow; border-radius : 50;")

    def resizeEvent(self, event):
        self.setMask(QRegion(self.rect(), QRegion.Ellipse))
        QPushButton.resizeEvent(self, event)


class PalmMenuButton(QPushButton):
    def __init__(self, parent=None, isTarget=False):
        super(PalmMenuButton, self).__init__(parent)
        self.isTarget = isTarget
        if isTarget:
            self.setStyleSheet("background-color : red")
        else:
            self.setStyleSheet("background-color : yellow;")


class PalmPadWindow(QDialog):
    def __init__(self, widget, tasks, serverQueue):
        super().__init__()
        self.setWindowTitle("PalmPad")
        self.setGeometry(100, 100, 600, 400)
        self.UiComponents()
        self.show()

        self.serverQueue = serverQueue
        self.handTrackingResults = "1, 1"
        self.handTrackingListener = Listener(self, serverQueue)
        self.handTrackingListener.isTouchSignal.connect(self.handTrackingHandler)
        self.handTrackingListener.start()

        self.widget = widget

        self.cursor = QCursor(Qt.ClosedHandCursor)
        self.setCursor(self.cursor)
        self.mouseX = 600
        self.mouseY = 600

        self.isOnButton = False

    # method for widgets
    def UiComponents(self):
        # creating a push button
        button = MouseClickButton(self)
        button.installEventFilter(self)
        button.setGeometry(200, 150, 100, 100)
        button.clicked.connect(self.clicked)

    def clicked(self):
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)


    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter or event.type() == QEvent.MouseButtonPress or event.type() == QEvent.ToolTip: #https://het.as.utexas.edu/HET/Software/PyQt/qevent.html
            print("on button")
            self.isOnButton = True
            return True
        else:
            print("NOT on button", event.type())
            self.isOnButton = False
            return False


    @pyqtSlot(str)
    def handTrackingHandler(self, result):
        results = result.split(",")
        # print("results: ", results)

        if results[0] == "0": #PalmPad
            self.mouseX, self.mouseY = self.cursor.pos().x(), self.cursor.pos().y()
            dx, dy = (float(results[1]), float(results[2]))
            
            try:
                dx = int(dx)
                dy = int(dy)
            except:
                dx = 0
                dy = 0

            if dx == 999 and dy == 999:
                if self.isOnButton:
                    self.clicked()
                
            else:
                self.mouseX -= dx
                self.mouseY += dy

                self.cursor.setPos(self.mouseX, self.mouseY)
            # print("dxy: ", dx, dy)


        # self.handTrackingResults = (int(results[0]), int(results[1]))
        # #self.handTrackingResults = result
        # self.repaint()


class PalmMenuWindow(QDialog):
    def __init__(self, widget, tasks, serverQueue):
        super().__init__()
        self.tasks = tasks
        self.target = (2, 2)
        self.buttons = [[0 for node in range(3)] for finger in range(1, 5)]
        self.setWindowTitle("PalmMenu")
        self.setGeometry(100, 100, 600, 400)
        self.UiComponents()
        self.show()

        self.serverQueue = serverQueue
        self.handTrackingResults = "1, 1"
        self.handTrackingListener = Listener(self, serverQueue)
        self.handTrackingListener.isTouchSignal.connect(self.handTrackingHandler)
        self.handTrackingListener.start()

        self.widget = widget
        self.serverQueue = serverQueue


    # method for widgets
    def UiComponents(self):
        width = 30
        height = 20
        xPadding = 10
        yPadding = 15

        for finger in range(1, 5):
            for node in range(3):
                isTarget = True if (finger == self.target[0] and node == self.target[1]) else False
                button = PalmMenuButton(self, isTarget)
                self.buttons[finger-1][node] = button
                # button.clicked.connect(self.clicked) # https://stackoverflow.com/questions/6784084/how-to-pass-arguments-to-functions-by-the-click-of-button-in-pyqt/42945033
                # button.connect(button, QtCore.SIGNAL('clicked()'), clicked(()))
                # print(isTarget)
                # button.clicked.connect(lambda: self.clicked(isTarget))
                # button.clicked.connect(lambda: self.clicked(self.buttons[finger-1][node]))
                button.setGeometry((width + xPadding)*node, (height + yPadding) * finger, width, height)

    # def clicked(self, button):
    #     if button.isTarget:
    #         self.widget.setCurrentIndex(self.widget.currentIndex()-1)
    #     else:
    #         pass

    def clicked(self):
        self.widget.setCurrentIndex(self.widget.currentIndex()-1)


    @pyqtSlot(str)
    def handTrackingHandler(self, result):
        results = result.split(",")
        # print("results: ", results)

        if results[0] == "1": #PalmMenu
            finger, node = (float(results[1]), float(results[2]))
            
            try:
                finger = int(finger)
                node = int(node)
            except:
                pass

            if finger == self.target[0] and node == self.target[1]:
                self.clicked() # TODO: clicked(button)??



if __name__ == "__main__":
    clientQueue = Queue()

    app = QApplication(sys.argv)

    widget = QStackedWidget()

    palmMenuTasks = [(finger, node) for finger in range(1, 5) for node in range(3)]
    palmPadTasks = [direction for direction in range(8)]

    random.shuffle(palmMenuTasks)
    random.shuffle(palmPadTasks)

    palmPadWindow = PalmPadWindow(widget, palmPadTasks, clientQueue)
    palmMenuWindow = PalmMenuWindow(widget, palmMenuTasks, clientQueue)

    widget.addWidget(palmPadWindow)
    widget.addWidget(palmMenuWindow)
    

    # root = tk.Tk()
    # widget.setFixedHeight(root.winfo_screenheight())
    # widget.setFixedWidth(root.winfo_screenwidth())
    widget.setFixedHeight(600)
    widget.setFixedWidth(1000)
    widget.show()

    app.exec_()
