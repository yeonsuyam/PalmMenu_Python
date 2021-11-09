import serial
from finger import Finger
from multiprocessing import Process, Queue

class TouchSensing():
    def __init__(self, touchSensingQueue, port="COM4", baudrate=115200, fingers=[2]):
        self.port = port
        self.baudrate = baudrate
        self.arduino = serial.Serial(port, baudrate)
        
        self.touchSensingQueue = touchSensingQueue
        
        self.fingers = {}
        for fingerNum in fingers:
            finger = Finger()
            self.fingers[fingerNum] = finger
        
        pass

   
    def getSensorData(self):
        while True:
            try:
                line = self.arduino.readline()
                line = str(line, 'utf-8').strip()
                fingerNum, touchSensorData = self.extractData(line)
            except KeyboardInterrupt:
                return
            except:
                pass
            else:
                self.updateTouchState(fingerNum, touchSensorData)
            pass


    def extractData(self, line):
        data = line.split(",")
        fingerNum = 2
        touchSensorData = int(data[0])
        #fingerNum = int(data[0])
        #touchSensorData = int(data[1])
        return fingerNum, touchSensorData


    def updateTouchState(self, fingerNum, touchSensorData):
        
        result = self.fingers[fingerNum].updateTouchState(touchSensorData) # 1 if TouchDown, 0 if TouchUp

        if result != None:
            self.touchSensingQueue.put((fingerNum, result))

        return

if __name__ == "__main__":
    q = Queue()
    touchSensing = TouchSensing(q, port="/dev/cu.usbserial-AL03KLV2", baudrate=115200)
    try:
        touchSensing.getSensorData()
    except KeyboardInterrupt:
        pass

