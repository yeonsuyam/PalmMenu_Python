import mediapipe as mp
import cv2
from handTracking2 import HandTracking
from touchSensing import TouchSensing
from multiprocessing import Process, Queue
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


def getImage(q):
    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)
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
    handTracking = HandTracking(imageQueue)
    
    #handTrackingProcess = Process(target=handTrackingFunction, args=(imageQueue, ))
    #handTrackingProcess.start()

    getImageProcess = Process(target=getImage, args=(imageQueue,))
    getImageProcess.start()

    try: 
        while True:
            print(handTracking.dominantHand.joints)
    except KeyboardInterrupt:
        pass

    getImageProcess.join()
