import mediapipe as mp
from google.protobuf.json_format import MessageToDict

from hand import Hand
from handTrackingCamera import HandTrackingCamera
import cv2 
import numpy as np
class HandTracking():
    def __init__(self, resultQueue):
        self.running = True

        mp_hands = mp.solutions.hands
        self.resultQueue = resultQueue
        # rightHand = Hand()
        # leftHand = Hand()
        # self.hands = {"left": leftHand, "right": rightHand}

        upperCameraHandler = mp_hands.Hands(
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        lowerCameraHandler = mp_hands.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        self.upperCamera = HandTrackingCamera(3, upperCameraHandler)
        self.lowerCamera = HandTrackingCamera(0, lowerCameraHandler)
        
        pass


    def run(self):
        rightHand = None
        leftHand = None
        while self.running:
            try:
                upperImage = self.upperCamera.updateHands()
                lowerImage = self.lowerCamera.updateHands()

            except:
                pass
            else:
                # print("isHandsOverlapped: ", self.upperCamera.isHandsOverlapped())
                if self.upperCamera.isHandsOverlapped():
                    rightHand = self.upperCamera.getRightHandJoints()
                    leftHand += self.lowerCamera.getLeftHandJointsDiff()

                else:
                    rightHand = self.upperCamera.getRightHandJoints()
                    leftHand = self.upperCamera.getLeftHandJoints()

            self.resultQueue.put({"Right": rightHand, "Left": leftHand})
            
            # if (upperImage != None and lowerImage)
            try:
                numpy_vertical_concat = np.concatenate((upperImage, lowerImage), axis=0)
                cv2.imshow('hands', numpy_vertical_concat)            
            except:
                pass
            if cv2.waitKey(5) & 0xFF == 27:
                break

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
        #print(dx * 10, dy * 10) 
        self.resultQueue.put("0," + str(dx) + "," + str(dy))

        return









