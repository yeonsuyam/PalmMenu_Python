import mediapipe as mp
from google.protobuf.json_format import MessageToDict

from hand import Hand
from multiprocessing import Process, Queue

class HandTracking():
    def __init__(self, imageQueue, dominantHandInfo = "Right"):
        self.dominantHandInfo = "Right"
        self.nonDominantHandInfo = "Left" if dominantHandInfo == "Right" else "Right"
        #self.isDominantHand = {dominantHand: 1, nonDominantHand: 0}

        #self.imageQueue = imageQueue

        dominantHandLandmarks = [8]
        nonDominantHandLandmarks = [i for i in range(5, 21)]
        
        self.dominantHand = Hand(self.dominantHandInfo, dominantHandLandmarks)
        self.nonDominantHand = Hand(self.nonDominantHandInfo, nonDominantHandLandmarks)
    
        #self.dominantHandJoints = [0, 0, 0]
        #self.nondominantHandJoints = [[0, 0, 0] for i in range(4 * 4)]
        #self.handJoints[self.nondominantHandJoints, self.dominantHandJoints]

        #self.handExtraction = mp.solutions.hands.Hands(
            #model_complexity=0,
            #max_num_hands=2,
            #min_detection_confidence=0.5,
            #min_tracking_confidence=0.5)
        
        getImageProcess = Process(target=self.getImage, args=(imageQueue,))
        getImageProcess.start()

        print("start getImageProcess in HandTracking")
        pass

    
    def getHand(self, handInfo):
        if handInfo == self.dominantHandInfo:
            return self.dominantHand
        elif handInfo == self.nonDominantHandInfo:
            return self.nonDominantHand
        pass

    def getImage(self, imageQueue):
        handExtraction = mp.solutions.hands.Hands(
            model_complexity=0,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        
        while True:
            try:
                image = imageQueue.get()
                results = handExtraction.process(image)
            except:
                continue
            else:
                self.updateFingerJoints(results)
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


    def updateFingerJoints(self, results):
        #def updateFingerJoints(self, image):
        #results = self.handExtraction.process(image)
       
        if results == None or results.multi_handedness == None:
            return
        if len(results.multi_handedness) > 2:
            print("Hand Tracking results: ", len(results.multi_handedness))

        for handInfo, handLandmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
            handInfoDict = MessageToDict(handInfo)["classification"][0]
            hand = self.getHand(handInfoDict["label"])
            hand.updateHandJoints(handLandmarks)
        return
