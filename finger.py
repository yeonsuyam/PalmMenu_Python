from enum import Enum

class TouchState(Enum):
    Touch = 1
    NotTouch = 0

class Finger():
    def __init__(self, threasholds={"up": 80, "down": 70}):
        self.threasholds = threasholds
        self.touchStates = TouchState.NotTouch

    def updateTouchState(self, touchSensorData):

        if self.touchStates == TouchState.NotTouch:
            if touchSensorData > self.threasholds["down"]:
                return self.touchDownEvent()
        elif self.touchStates == TouchState.Touch:
            if touchSensorData < self.threasholds["up"]:
                return self.touchUpEvent()


    def touchDownEvent(self):
        print("touchDown")
        self.touchStates = TouchState.Touch
        return 1 

    def touchUpEvent(self):
        print("touchUp")
        self.touchStates = TouchState.NotTouch
        return 0
