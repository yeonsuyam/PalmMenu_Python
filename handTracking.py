import mediapipe as mp
from google.protobuf.json_format import MessageToDict

from hand import Hand

class HandTracking():
    def __init__(self, imageQueue, resultQueue, results = [("index", "palmPad")], dominantHandInfo = "Right"):
        self.dominantHandInfo = dominantHandInfo
        self.nonDominantHandInfo = "Left" if dominantHandInfo == "Right" else "Right"
        #self.isDominantHand = {dominantHand: 1, nonDominantHand: 0}

        self.imageQueue = imageQueue
        self.resultQueue = resultQueue

        self.funcName2Func = {"nearestJoint": self.getNearestJoint, "palmPad": self.palmPad}
        self.fingerName2Landmark = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
        self.returnFunctions = [(self.funcName2Func[funcName], self.fingerName2Landmark[fingerName]) for (fingerName, funcName) in results] # self.getNearestJoint, 8

        print("Return Functions: ", self.returnFunctions)

        #dominantHandLandmarks = [self.fingerName2Landmark(fingerName) for (fingerName, _) in results]
        #nonDominantHandLandmarks = [i for i in range(5, 21)]
        
        #self.dominantHand = Hand(self.dominantHandInfo, dominantHandLandmarks)
        #self.nonDominantHand = Hand(self.nonDominantHandInfo, nonDominantHandLandmarks)
    
        self.dominantHand = Hand(self.dominantHandInfo)
        self.nonDominantHand = Hand(self.nonDominantHandInfo)
        
        #self.dominantHandJoints = [0, 0, 0]
        #self.nondominantHandJoints = [[0, 0, 0] for i in range(4 * 4)]
        #self.handJoints[self.nondominantHandJoints, self.dominantHandJoints]

        self.handExtraction = mp.solutions.hands.Hands(
            model_complexity=0,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        pass


    def run(self): #results = [[fingerNum, functionName], [fingerNum, functionName], ..]
        while True:
            try:
                image = self.imageQueue.get()
            except:
                continue
            else:
                isRightHand = self.updateFingerJoints(image)
                if isRightHand:
                    [func(param) for func, param in self.returnFunctions]


    def getImage(self):
        while True:
            try:
                image = self.imageQueue.get()
            except:
                continue
            else:
                self.updateFingerJoints(image)
            pass


    def getResult(self):
        while True:
            try:
                result = self.imageQueue.get()
            except:
                continue
            else:
                self.updateFingerJoints(result)
            pass


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
        print(handInfo)
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









