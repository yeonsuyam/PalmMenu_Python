import mediapipe as mp
from google.protobuf.json_format import MessageToDict

from hand import Hand
import cv2
import numpy as np

class HandTrackingCamera():
    def __init__(self, cameraId, handTrackingHandler):
        self.camera = cv2.VideoCapture(cameraId)
        self.handTrackingHandler = handTrackingHandler

        rightHand = Hand("Right")
        leftHand = Hand("Left")
        self.hands = {"Left": leftHand, "Right": rightHand}
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        pass


    def updateHands(self):
        image = None

        try:
            success, image = self.camera.read()
            if not success:
                print("No Camera")
            else:
                image.flags.writeable = False
                image = cv2.flip(image, 1)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_height, image_width, _ = image.shape

                results = self.handTrackingHandler.process(image)
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                for handInfo, handLandmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
                    handName = MessageToDict(handInfo)["classification"][0]["label"]
                    self.hands[handName].updateHandJoints(handLandmarks, image_height, image_width)


                    self.mp_drawing.draw_landmarks(
                        image,
                        handLandmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())


        except:
            pass
        # else:
        #     pass
        #     # cv2.imshow('Hands', image)
        return image

    def isHandsOverlapped(self):
        leftHandpinkyEdge = self.hands["Left"].getPinkyEdge() # ([x, y, z], [x, y, z])
        rightHandIndexEdge = self.hands["Right"].getIndexEdge()
        rightHandUpperEdge = self.hands["Right"].getUpperEdge()
        rightHandpinkyEdge = self.hands["Right"].getPinkyEdge()


        if self.isTwoLineOverlapped(leftHandpinkyEdge, rightHandIndexEdge):
            return True
        if self.isTwoLineOverlapped(leftHandpinkyEdge, rightHandUpperEdge):
            return True
        if self.isTwoLineOverlapped(leftHandpinkyEdge, rightHandpinkyEdge):
            return True 
        return False


    def isTwoLineOverlapped(self, line1, line2):
        # https://gaussian37.github.io/math-algorithm-line_intersection/
        p1, p2 = line1
        p3, p4 = line2

        if self.counterClockWise(p1, p2, p3) * self.counterClockWise(p1, p2, p4) < 0 and self.counterClockWise(p3, p4, p1) * self.counterClockWise(p3, p4, p2) < 0:
            return True
        else:
            return False


    def counterClockWise(self, p1, p2, p3):
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)

        if np.cross(v1, v2) > 0:
            return 1
        else:
            return -1

    def getRightHandJoints(self):
        return self.hands["Right"].getJoints()

    def getLeftHandJoints(self):
        return self.hands["Left"].getJoints()

    def getRightHandJointsDiff(self):
        return self.hands["Right"].calculateHandDiff()

    def getLeftHandJointsDiff(self):
        return self.hands["Left"].calculateHandDiff()



if __name__ == "__main__":
    mp_hands = mp.solutions.hands
    upperCameraHandler = mp_hands.Hands(
        max_num_hands=2,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)  

    upperCamera = HandTrackingCamera(3, upperCameraHandler)

    for i in range(10000):
        upperCamera.updateHands()

        if cv2.waitKey(5) & 0xFF == 27:
            break










