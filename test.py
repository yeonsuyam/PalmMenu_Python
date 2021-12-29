# importing libraries
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
  

class HoverButton(QPushButton):
    def __init__(self, parent=None):
        super(HoverButton, self).__init__(parent)
        self.setStyleSheet("background-color : yellow; border-radius : 50;")

    def resizeEvent(self, event):
        self.setMask(QRegion(self.rect(), QRegion.Ellipse))
        QPushButton.resizeEvent(self, event)



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
  
        # setting title
        self.setWindowTitle("Python ")
  
        # setting geometry
        self.setGeometry(100, 100, 600, 400)
  
        # calling method
        self.UiComponents()
  
        # showing all the widgets
        self.show()

    def UiComponents(self):
        button = HoverButton(self)
        button.setGeometry(200, 150, 100, 100)
        button.clicked.connect(self.clickme)
  
    # action method
    def clickme(self):
        # printing pressed
        print("pressed")
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
  
# start the app
sys.exit(App.exec())