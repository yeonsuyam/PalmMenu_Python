import mediapipe as mp
from google.protobuf.json_format import MessageToDict

from hand import Hand
from handTrackingCamera import HandTrackingCamera
import cv2 
import numpy as np
from multiprocessing import Process, Queue

import time

class HandTracking():
    def __init__(self, upperCameraQueue, lowerCameraQueue, resultQueue):
        self.running = True
        self.upperCameraQueue = upperCameraQueue
        self.lowerCameraQueue = lowerCameraQueue
        self.resultQueue = resultQueue

        self.upperCamera = HandTrackingCamera(None, 3, handNum = 1)
        self.lowerCamera = HandTrackingCamera(None, 0, handNum = 2)
        pass


    def run(self):
        rightHand = None
        leftHand = None

        while self.running:
            upperCameraHandTrackingResult = None
            lowerCameraHandTrackingResult = None

            # try:
            #     lowerCameraHandTrackingResult = self.lowerCameraQueue.get(0)
            #     hand = lowerCameraHandTrackingResult["Right"] if lowerCameraHandTrackingResult["Right"] is not None else lowerCameraHandTrackingResult["Left"]
            #     self.lowerCamera.hands["Left"].updateHandByNPArray(hand)
            # except:
            #     pass


            try:
                upperCameraHandTrackingResult = self.upperCameraQueue.get(0)

                if upperCameraHandTrackingResult["Left"] is None and upperCameraHandTrackingResult["Right"] is not None:
                    self.upperCamera.hands["Left"].updateHandByNPArray(upperCameraHandTrackingResult["Right"])
                    self.upperCamera.hands["Right"].updateHandByNPArray(None)
                else:
                    self.upperCamera.hands["Right"].updateHandByNPArray(upperCameraHandTrackingResult["Right"])
                    self.upperCamera.hands["Left"].updateHandByNPArray(upperCameraHandTrackingResult["Left"])
            except:
                pass

            if upperCameraHandTrackingResult == None and lowerCameraHandTrackingResult == None:
                continue

            # startTime = time.time()

            rightHand = self.upperCamera.getRightHandJoints()
            leftHand = self.upperCamera.getLeftHandJoints()
            # if self.upperCamera.isHandsOverlapped():
            #     # print("handTracking2.py, isHandsOverlapped")
            #     rightHand = self.upperCamera.getRightHandJoints()
            #     if leftHand.size is not None:
            #         leftHand += self.lowerCamera.getLeftHandJointsDiff()

            # else:
            #     # print("handTracking2.py, NOT Overlapped")
            #     rightHand = self.upperCamera.getRightHandJoints()
            #     leftHand = self.upperCamera.getLeftHandJoints()


            self.resultQueue.put({"Right": rightHand, "Left": leftHand})
                
        return


    def exit(self):
        self.running = False
        return


    def updateFingerJoints(self, image):
        isDominantHand = False

        image_height, image_width, _ = image.shape
        results = self.handExtraction.process(image)
       
        if results == None or results.multi_handedness == None:
            return False
        
        handCNT = len(results.multi_handedness)

        for handInfo, handLandmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
            handInfoDict = MessageToDict(handInfo)["classification"][0]
            handName = handInfoDict["label"]
                
            if handName == self.nonDominantHandInfo and handCNT == 1:
                hand = self.nonDominantHand
                hand.updateHandJoints(handLandmarks, image_height, image_width)
            elif handName == self.dominantHandInfo:
                hand = self.dominantHand
                hand.updateHandJoints(handLandmarks, image_height, image_width)
                isDominantHand = True
        return isDominantHand



    def getHand(self, handInfo):
        if handInfo == self.dominantHandInfo:
            return self.dominantHand
        elif handInfo == self.nonDominantHandInfo:
            return self.nonDominantHand
        pass


    def getNearestJoint(self, fingerLandmark):
        dominantFingerXYZ = self.dominantHand.getFingerXYZ(fingerLandmark)
        result = self.nonDominantHand.calculateNearestFingerNode(dominantFingerXYZ) # 3, 3
        self.resultQueue.put("1," + str(result[0]) + "," + str(result[1])) # "3, 3"
        
        return


    def calculatePlaneXYZ(self):
        x = nonDominantHand.getPlane()

    def palmPad(self, fingerLandmark):
        dominantFingerXYZ = self.dominantHand.getFingerXYZ(fingerLandmark)

        dx, dy = self.nonDominantHand.calculateDXYFromPalm(dominantFingerXYZ) 
        self.resultQueue.put("0," + str(dx) + "," + str(dy))

        return




def upperCameraUpdateHands(upperImageQueue):
    upperCamera = HandTrackingCamera(3, handNum = 2)
    upperCamera.updateHands(upperImageQueue)

def lowerCameraUpdateHands(lowerImageQueue):
    lowerCamera = HandTrackingCamera(0, handNum = 1)
    lowerCamera.updateHands(lowerImageQueue)






