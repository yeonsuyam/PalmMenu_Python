import mediapipe as mp
import cv2
from handTracking2 import HandTracking
from handTrackingCamera import HandTrackingCamera
from touchSensing import TouchSensing
from multiprocessing import Process, Queue
#from userStudy1 import UserStudy1
from userStudy1Client2 import PalmPadWindow, PalmMenuWindow
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


def userStudy1Function(handTrackingQueue, touchSensingQueue, palmPadResultQueue, palmMenuResultQueue):
    userStudy1 = UserStudy1(handTrackingQueue, touchSensingQueue, palmPadResultQueue, palmMenuResultQueue)
    userStudy1.run()


class State(Enum):
    Default = 0
    PalmPad = 1
    PalmMenu = 2


class UserStudy1():
    def __init__(self, handTrackingQueue, touchSensingQueue, palmPadResultQueue, palmMenuResultQueue, dominantHandInfo = "Right"):
        self.running = True
        self.state = State.PalmPad

        self.palmPad = PalmPad(handTrackingQueue, touchSensingQueue, palmPadResultQueue, palmMenuResultQueue)
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
    def __init__(self, handTrackingResultQueue, touchSensingResultQueue, palmPadResultQueue, palmMenuResultQueue, dominantHandInfo = "Right"):
        self.handTrackingResultQueue = handTrackingResultQueue
        self.touchSensingResultQueue = touchSensingResultQueue
        self.palmPadResultQueue = palmPadResultQueue
        self.palmMenuResultQueue = palmMenuResultQueue


        self.rightHand = Hand("Right")
        self.leftHand = Hand("Left")
        self.hands = {"Right": self.rightHand, "Left": self.leftHand}
        self.touchsensingResult = False

        self.dominantHandInfo = dominantHandInfo
        self.nonDominantHandInfo = "Left" if dominantHandInfo == "Right" else "Right"
        self.dominantHandFinger = "index" # Index Finger

        self.functions = {State.PalmPad: self.palmPad, State.PalmMenu: self.palmMenu}
        self.isCalculateDXYAfterTouchDown = False



    def calculate(self, state):
        startTime = time.time()
        success = self.updateHand()

        if success:
            # self.functions[state]()
            self.palmPad()
            self.palmMenu()

        startTime = time.time()

        return


    def updateHand(self):
        try:
            touchsensingResult = self.touchSensingResultQueue.get(0)
        except:
            pass
        else:
            self.touchsensingResult = touchsensingResult
        try:
            handTrackingResult = self.handTrackingResultQueue.get(0)
        except:
            pass
        else:
            if handTrackingResult is not None:
                self.hands["Right"].updateHandByNPArray(handTrackingResult["Right"])
                self.hands["Left"].updateHandByNPArray(handTrackingResult["Left"])
            return True


    def dominantHand(self):
        return self.hands[self.dominantHandInfo]

    def nonDominantHand(self):
        return self.hands[self.nonDominantHandInfo]


    def addAcceleration(self, dx, dy):
        if dx == 0 and dy == 0:
            return 0, 0
        else:
            dt = time.time() - self.updateTime
            self.updateTime = time.time()
            
        speed = (dx ** 2 + dy ** 2) ** 0.5 / dt

        # print("[UserStudy1.py] dx: ", dx, " / dy: ", dy, " / dt: ", dt, " / speed: ", speed)
        print("[UserStudy1.py] dt: ", dt, " / speed: ", speed)
        if (speed < 10):
            accFactor = (1.3 / 10) * speed
        elif (speed < 130):
            accFactor = 1.3
        elif (speed < 430):
            accFactor = (3.2 / 300) * (speed - 130) + 1.3
        else:
            accFactor = 4.5

        return dx * accFactor, dy * accFactor


    def palmPad(self):
        # print("palmPAD")

        # if self.touchsensingResult == 2: # Touch Down State
        #     self.palmPadResultQueue.put("0," + str(dx) + "," + str(dy) + "\n")
        #     return
        
        if self.touchsensingResult == 1: # Touch Down Event
            dominantFingerXYZ = self.dominantHand().getFingerXYZByName(self.dominantHandFinger)
            dx, dy = self.nonDominantHand().calculateDXYFromPalm(dominantFingerXYZ)
            dx, dy = self.addAcceleration(dx, dy)
            
            if self.isCalculateDXYAfterTouchDown:
                self.palmPadResultQueue.put("0," + str(dx) + "," + str(dy) + "\n")
            else:
                print("0," + str(dx) + "," + str(dy) + "\n")

            self.isCalculateDXYAfterTouchDown = True
            return

        elif self.touchsensingResult == -1: # Tap
            self.touchsensingResult = 0
            self.palmPadResultQueue.put("0,999,999")
            self.isCalculateDXYAfterTouchDown = False
            pass

        elif self.touchsensingResult == 0: # Touch Up
            self.isCalculateDXYAfterTouchDown = False
        # return "0," + str(dx) + "," + str(dy)


    def palmMenu(self):
        # print("palmMENU")
        dominantFingerXYZ = self.dominantHand().getFingerXYZByName(self.dominantHandFinger)
        if dominantFingerXYZ is None:
            return

        result = self.nonDominantHand().calculateNearestFingerNode(dominantFingerXYZ) # 3, 3
        if self.touchsensingResult == 2:
            self.palmMenuResultQueue.put("1," + str(result[0]) + "," + str(result[1]) + "\n") # "3, 3"
            # print("[UserStudy1.py]" + "1," + str(result[0]) + "," + str(result[1]) + "\n")
        # return "1," + str(result[0]) + "," + str(result[1])

 

if __name__ == '__main__':
    upperCameraQueue = Queue()
    lowerCameraQueue = Queue()
    handTrackingResultQueue = Queue()
    touchSensingResultQueue = Queue()
    palmPadResultQueue = Queue()
    palmMenuResultQueue = Queue()

    upperCameraProcess = Process(target=handTrackingUpperCameraFunction, args=(upperCameraQueue,))
    lowerCameraProcess = Process(target=handTrackingLowerCameraFunction, args=(lowerCameraQueue,))
    handTrackingProcess = Process(target=handTrackingFunction, args=(upperCameraQueue, lowerCameraQueue, handTrackingResultQueue,))
    touchSensingProcess = Process(target=touchSensingFunction, args=(touchSensingResultQueue,))    
    userStudy1Process = Process(target=userStudy1Function, args=(handTrackingResultQueue, touchSensingResultQueue, palmPadResultQueue, palmMenuResultQueue, ))

    upperCameraProcess.start()
    lowerCameraProcess.start()
    handTrackingProcess.start()
    touchSensingProcess.start()
    userStudy1Process.start()

    App = QApplication(sys.argv)

    widget = QStackedWidget()

    palmMenuTasks = [(finger, node) for finger in range(1, 5) for node in range(3)]
    palmPadTasks = [direction for direction in range(8)]

    random.shuffle(palmMenuTasks)
    random.shuffle(palmPadTasks)

    palmPadWindow = PalmPadWindow(widget, palmPadTasks, palmPadResultQueue)
    palmMenuWindow = PalmMenuWindow(widget, palmMenuTasks, palmMenuResultQueue)

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
    touchSensingProcess.join()
    userStudy1Process.join()
