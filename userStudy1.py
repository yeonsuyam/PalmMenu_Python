import mediapipe as mp
import cv2
from handTracking2 import HandTracking
from handTrackingCamera import HandTrackingCamera
from touchSensing import TouchSensing
from multiprocessing import Process, Queue
#from userStudy1 import UserStudy1
from userStudy1Client2 import Window, PalmPadWindow, PalmMenuWindow
from palmPadClient import Window
from PyQt5 import QtGui
from PyQt5.QtWidgets import * 
import random
import sys
from enum import Enum
from hand import Hand

import time

def handTrackingFunction(upperCameraQueue, lowerCameraQueue, resultQueue):
    handTracking = HandTracking(upperCameraQueue, lowerCameraQueue, resultQueue)
    handTracking.run()

def handTrackingUpperCameraFunction(upperCameraQueue):
    handTrackingCamera = HandTrackingCamera(upperCameraQueue, 0, handNum = 2)
    handTrackingCamera.updateHands()

def handTrackingLowerCameraFunction(lowerCameraQueue):
    handTrackingCamera = HandTrackingCamera(lowerCameraQueue, 3, handNum = 1)
    handTrackingCamera.updateHands()


def touchSensingFunction(q):
    touchSensing = TouchSensing(q, port="/dev/cu.usbserial-AL03KLV2", baudrate=115200)
    touchSensing.getSensorData()


def userStudy1Function(handTrackingQueue, touchSensingQueue, resultQueue):
    userStudy1 = UserStudy1(handTrackingQueue, touchSensingQueue, resultQueue)
    userStudy1.run()


class State(Enum):
    Default = 0
    PalmPad = 1
    PalmMenu = 2


class UserStudy1():
    def __init__(self, handTrackingQueue, touchSensingQueue, resultQueue, dominantHandInfo = "Right"):
        self.running = True
        self.state = State.PalmPad

        self.palmPad = PalmPad(handTrackingQueue, touchSensingQueue, resultQueue)
        # self.palmMenu = PalmMenu(handTrackingQueue)
        # self.handProcessing = {State.PalmPad: self.palmPad, State.PalmMenu: self.palmMenu}

        self.handTrackingQueue = handTrackingQueue
        self.touchSensingQueue = touchSensingQueue


    def initTask(self):
        pass


    def run(self):
        while self.running:
            self.palmPad.calculate(self.state)

            # try:
            #     self.touchSensingQueue.get()
            # except:
            #     pass
            # else:
            #     pass

class PalmPad():
    def __init__(self, handTrackingResultQueue, touchSensingResultQueue, resultQueue, dominantHandInfo = "Right"):
        self.handTrackingResultQueue = handTrackingResultQueue
        self.touchSensingResultQueue = touchSensingResultQueue
        self.resultQueue = resultQueue

        self.rightHand = Hand("Right")
        self.leftHand = Hand("Left")
        self.hands = {"Right": self.rightHand, "Left": self.leftHand}
        self.touchsensingResult = True

        self.dominantHandInfo = dominantHandInfo
        self.nonDominantHandInfo = "Left" if dominantHandInfo == "Right" else "Right"
        self.dominantHandFinger = "index" # Index Finger

        self.functions = {State.PalmPad: self.palmPad, State.PalmMenu: self.palmMenu}


    def calculate(self, state):
        startTime = time.time()
        success = self.updateHand()

        if success:
            self.functions[state]()

        startTime = time.time()

        return


    def updateHand(self):
        try:
            handTrackingResult = self.handTrackingResultQueue.get(0)
        except:
            return False
        else:
            self.hands["Right"].updateHandByNPArray(handTrackingResult["Right"])
            self.hands["Left"].updateHandByNPArray(handTrackingResult["Left"])

        # try:
        #     touchsensingResult = self.touchSensingResultQueue.get(0)
        # except:
        #     pass
        # else:
        #     self.touchsensingResult = int(touchsensingResult)


            return True


    def dominantHand(self):
        return self.hands[self.dominantHandInfo]

    def nonDominantHand(self):
        return self.hands[self.nonDominantHandInfo]


    def palmPad(self):
        dominantFingerXYZ = self.dominantHand().getFingerXYZByName(self.dominantHandFinger)
        dx, dy = self.nonDominantHand().calculateDXYFromPalm(dominantFingerXYZ) 
        if self.touchsensingResult:
            self.resultQueue.put("0," + str(dx) + "," + str(dy))

        # return "0," + str(dx) + "," + str(dy)


    def palmMenu(self):
        dominantFingerXYZ = self.dominantHand().getFingerXYZByName(fingerLandmark)
        result = self.nonDominantHand().calculateNearestFingerNode(dominantFingerXYZ) # 3, 3
        if self.touchsensingResult:
            self.resultQueue.put("1," + str(result[0]) + "," + str(result[1])) # "3, 3"
        
        # return "1," + str(result[0]) + "," + str(result[1])



if __name__ == '__main__':
    upperCameraQueue = Queue()
    lowerCameraQueue = Queue()
    handTrackingResultQueue = Queue()
    touchSensingResultQueue = Queue()
    clientQueue = Queue()

    upperCameraProcess = Process(target=handTrackingUpperCameraFunction, args=(upperCameraQueue,))
    lowerCameraProcess = Process(target=handTrackingLowerCameraFunction, args=(lowerCameraQueue,))
    handTrackingProcess = Process(target=handTrackingFunction, args=(upperCameraQueue, lowerCameraQueue, handTrackingResultQueue,))
    # touchSensingProcess = Process(target=touchSensingFunction, args=(touchSensingResultQueue,))    
    userStudy1Process = Process(target=userStudy1Function, args=(handTrackingResultQueue, touchSensingResultQueue, clientQueue))

    upperCameraProcess.start()
    lowerCameraProcess.start()
    handTrackingProcess.start()
    # touchSensingProcess.start()
    userStudy1Process.start()

    App = QApplication(sys.argv)

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

    sys.exit(App.exec_())


    handTrackingProcess.join()
    # touchSensingProcess.join()
    userStudy1Process.join()
