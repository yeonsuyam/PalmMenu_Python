from enum import Enum
import time

class TouchState(Enum):
    Touch = 1
    NotTouch = 0

class Finger():
    def __init__(self, threasholds={"up": 67, "down": 64}):
        self.threasholds = threasholds
        self.touchStates = TouchState.NotTouch

        # For detecting tap
        self.touchDownTimer = time.time()

    def updateTouchState(self, touchSensorData):
        if self.touchStates == TouchState.NotTouch:
            if touchSensorData > self.threasholds["up"]:
                return self.touchDownEvent()
            # else:
            #     return self.touchUpEvent()
        elif self.touchStates == TouchState.Touch:
            if touchSensorData < self.threasholds["down"]:
                return self.touchUpEvent()
            # else:
            #     return self.touchDownState()

    def touchDownState(self):
        # print("touchDownState")
        self.touchDownTimer = time.time()        
        self.touchStates = TouchState.Touch
        return 2

    def touchDownEvent(self):
        # print("touchDown")
        self.touchDownTimer = time.time()        
        self.touchStates = TouchState.Touch
        return 1 

    def touchUpEvent(self):
        # print("touchUp")
        self.touchStates = TouchState.NotTouch
        if time.time() - self.touchDownTimer < 150 * 0.001:
            return -1 #Tap
        else:
            return 0
