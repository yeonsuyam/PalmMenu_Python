import mediapipe as mp
import cv2
from handTracking import HandTracking
from touchSensing import TouchSensing
from multiprocessing import Process, Queue
#from userStudy1 import UserStudy1
from view import Window
from PyQt5.QtWidgets import QApplication
import sys


def getImage(q):
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(1)
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        while cap.isOpened():
            success, image = cap.read()

            if not success:
                print("Empty camera frame")
            else:
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.flip(image, 1)
                results = hands.process(image)
                q.put(image)

def handTrackingFunction(q):
    handTracking = HandTracking(imageQueue = q)
    handTracking.getImage()

def touchSensingFunction(q):
    touchSensing = TouchSensing(q, port="/dev/cu.usbserial-AL03KLV2", baudrate=115200)
    touchSensing.getSensorData()


if __name__ == '__main__':
    imageQueue = Queue() 
    handTrackingProcess = Process(target=handTrackingFunction, args=(imageQueue, ))
    handTrackingProcess.start()

    getImageProcess = Process(target=getImage, args=(imageQueue,))
    getImageProcess.start()

    touchSensingQueue = Queue()
    touchSensingProcess = Process(target=touchSensingFunction, args=(touchSensingQueue, ))
    touchSensingProcess.start()

    #userStudy1 = UserStudy1(imageQueue, touchSensingQueue, )

    App = QApplication(sys.argv)
    window = Window(touchSensingQueue)
    sys.exit(App.exec_())

     

    #try:
        #while True:
            #result = touchSensingQueue.get()
    #except:
        #pass

    handTrackingProcess.join()
    getImageProcess.join()
    touchSensingProcess.join()
