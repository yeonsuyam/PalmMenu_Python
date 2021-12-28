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


        # upperImageQueue = Queue()
        # lowerImageQueue = Queue()

        # upperCamera = HandTrackingCamera(3, handNum = 2)
        # lowerCamera = HandTrackingCamera(0, handNum = 1)

        # upperImageProcess = Process(target=upperCamera.updateHands, args=(upperImageQueue,))
        # lowerImageProcess = Process(target=lowerCamera.updateHands, args=(lowerImageQueue,))

        # upperImageProcess.start()
        # lowerImageProcess.start()


        # upperImageProcess = Process(target=upperCameraUpdateHands, args=(upperImageQueue,))
        # lowerImageProcess = Process(target=lowerCameraUpdateHands, args=(lowerImageQueue,))
        # upperImageProcess.start()
        # lowerImageProcess.start()

        while self.running:
            upperCameraHandTrackingResult = None
            lowerCameraHandTrackingResult = None

            try:
                lowerCameraHandTrackingResult = self.lowerCameraQueue.get(0)
                hand = lowerCameraHandTrackingResult["Right"] if lowerCameraHandTrackingResult["Right"] is not None else lowerCameraHandTrackingResult["Left"]
                # self.lowerCamera.hands["Right"].updateHandByNPArray(lowerCameraHandTrackingResult["Right"])
                # self.lowerCamera.hands["Left"].updateHandByNPArray(lowerCameraHandTrackingResult["Left"])
                self.lowerCamera.hands["Left"].updateHandByNPArray(hand)
            except:
                pass
            try:
                upperCameraHandTrackingResult = self.upperCameraQueue.get(0)
                # if upperCameraHandTrackingResult["Right"] is None and lowerCameraHandTrackingResult["Right"] is not None:
                #     self.upperCamera.hands["Right"].updateHandByNPArray(upperCameraHandTrackingResult["Left"])
                #     self.upperCamera.hands["Left"].updateHandByNPArray(upperCameraHandTrackingResult["Right"])

                # elif upperCameraHandTrackingResult["Left"] is None and lowerCameraHandTrackingResult["Left"] is not None:
                #     self.upperCamera.hands["Left"].updateHandByNPArray(upperCameraHandTrackingResult["Right"])
                #     self.upperCamera.hands["Right"].updateHandByNPArray(upperCameraHandTrackingResult["Left"])
                # elif upperCameraHandTrackingResult["Right"] is not None and upperCameraHandTrackingResult["Left"] is not None:

                # else:
                #     self.upperCamera.hands["Right"].updateHandByNPArray(upperCameraHandTrackingResult["Right"])
                #     self.upperCamera.hands["Left"].updateHandByNPArray(upperCameraHandTrackingResult["Left"])


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

            if self.upperCamera.isHandsOverlapped():
                print("handTracking2.py, isHandsOverlapped")
                rightHand = self.upperCamera.getRightHandJoints()
                if leftHand.size != 0:
                    leftHand += self.lowerCamera.getLeftHandJointsDiff()

            else:
                print("handTracking2.py, NOT Overlapped")
                rightHand = self.upperCamera.getRightHandJoints()
                leftHand = self.upperCamera.getLeftHandJoints()


            self.resultQueue.put({"Right": rightHand, "Left": leftHand})
            
            # if (upperImage != None and lowerImage)
            # try:
            #     numpy_vertical_concat = np.concatenate((upperImage, lowerImage), axis=0) # concat 0.02
            #     cv2.imshow('hands', numpy_vertical_concat)            
            # except:
            #     pass
            # if cv2.waitKey(5) & 0xFF == 27:
            #     break



            # startTime = time.time()
                
        return


    def exit(self):
        self.running = False
        return


    #def updateFingerJoints(self, result):
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






