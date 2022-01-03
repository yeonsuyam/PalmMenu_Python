import math
import numpy as np

class Hand():
    def __init__(self, handInfo, landmarks=[i for i in range(21)]):
        self.handInfo = handInfo # Right | Left
        self.landmarks = landmarks
        self.joints = {i: [0, 0, 0] for i in landmarks}
        self.jointsDiff = {i: [0, 0, 0] for i in landmarks}
        self.landmarksInfo = {"thumbs": [i for i in range(1, 5)], 
                                "index": [i for i in range(5, 9)], 
                                "middle": [i for i in range(9, 13)], 
                                "ring": [i for i in range(13, 17)], 
                                "pinky": [i for i in range(17, 21)]}

        self.x = 0
        self.y = 0


    def updateHandByNPArray(self, npArray):
        if npArray is None:
            for landmark in self.landmarks:
                for xyz in range(3):
                    self.jointsDiff[landmark][xyz] = 0
            return

        for landmark in self.landmarks:
            for xyz in range(3):
                self.jointsDiff[landmark][xyz] = npArray[landmark][xyz] - self.joints[landmark][xyz]
                self.joints[landmark][xyz] = npArray[landmark][xyz]
        return


    def updateHandJoints(self, handLandmarks, h, w):
        for landmark in self.landmarks:
            self.jointsDiff[landmark][0] = handLandmarks.landmark[landmark].x * w - self.joints[landmark][0]
            self.jointsDiff[landmark][1] = handLandmarks.landmark[landmark].y * h - self.joints[landmark][1]
            self.jointsDiff[landmark][2] = handLandmarks.landmark[landmark].z - self.joints[landmark][2]

            self.joints[landmark][0] = handLandmarks.landmark[landmark].x * w
            self.joints[landmark][1] = handLandmarks.landmark[landmark].y * h
            self.joints[landmark][2] = handLandmarks.landmark[landmark].z
        

    def getFingerXYZ(self, landmarkNum):
        if not self.getJoints().any():
            return None
        else:
            return self.joints[landmarkNum]


    def getFingerXYZByName(self, name):
        if not self.getJoints().any():
            return None
        return self.joints[self.landmarksInfo[name][-1]]
    

    def calculateNearestFingerNode(self, targetXYZ):
        return self.calculateNearestFingerNodeByNearestNearestAlgorithm(targetXYZ)

    def calculateDXYFromPalm(self, fingerXYZ):
        if fingerXYZ is None:
            return (0, 0)

        # Calculate plane
        joints = self.joints

        xVector, yVector = self.calculateXYVector(joints)
        pointVector = np.array(fingerXYZ) - np.array(joints[0])

        if not np.any(xVector) or not np.any(yVector):
            return (0, 0)

        x, y = self.calculateProjectedVectorSize(xVector, yVector, pointVector)
       
        dx = self.x - x
        dy = self.y - y

        self.x = x
        self.y = y
        
        if dx ** 2 + dy ** 2 > 30 ** 2: 
            return (0, 0)
        else:
            return (dx, dy)


    def calculateXYVector(self, joints):
        xVector = np.array(joints[13]) - np.array(joints[0]) # fourth finger
        yVector = np.array(joints[5]) - np.array(joints[17])

        return xVector, yVector


    def calculateProjectedVectorSize(self, xVector, yVector, pointVector):
        # pointVectorProjectedX = np.dot(xVector, pointVector) / (np.dot(xVector, xVector)) ** 0.5
        # pointVectorProjectedY = np.dot(yVector, pointVector) / (np.dot(yVector, yVector)) ** 0.5

        # x = np.dot(pointVectorProjectedX, pointVectorProjectedX) ** 0.5
        # y = np.dot(pointVectorProjectedY, pointVectorProjectedY) ** 0.5 

        x = np.dot(xVector, pointVector) / np.dot(xVector, xVector) * 100
        y = np.dot(yVector, pointVector) / np.dot(yVector, yVector) * 100

        return x, y


    def calculateHandDiff(self):
        # TODO[]
        # Get last XY Axis
        lastJoints = {i: [0, 0, 0] for i in self.landmarks}
        handDiff = {i: [0, 0, 0] for i in self.landmarks}
        handDiffArray = np.empty((0, 3), float)
        joints = self.joints

        # Calculate lastJoint
        for landmark in self.landmarks:
            for i in range(3):
                lastJoints[landmark][i] = joints[landmark][i] - self.jointsDiff[landmark][i]

        # Calculate xyVector of last Joint
        xVector, yVector = self.calculateXYVector(lastJoints)

        for landmark in self.landmarks:
            handDiff[landmark][0], handDiff[landmark][1] = self.calculateProjectedVectorSize(xVector, yVector, np.array(self.jointsDiff[landmark]))

        # Change to np format
        for landmark in self.landmarks:
            handDiffArray = np.append(handDiffArray, np.array([handDiff[landmark]]), axis=0)

        return handDiffArray





    def calculateNearestFingerNodeByAngle(self, targetXYZ):
        jointLandmarks = [(i, i+1) for i in range(5, 8)] + [(i, i+1) for i in range(9, 12)] + [(i, i+1) for i in range(13, 16)] + [(i, i+1) for i in range(17, 20)]
        angles = self.calculateAngle(targetXYZ, jointLandmarks)

        # MaxAngleJoint
        vertexsOfNearestNode = [k for k,v in angles.items() if max(angles.values()) == v][0]
        nearestNode = vertexsOfNearestNode[0]//4, vertexsOfNearestNode[0]%4 - 1 # 3, 3 (middleFinger, third)

        return nearestNode


    def calculateAngle(self, fingerXYZ, jointLandmarks):
        angles = {}
        for landmark1, landmark2 in jointLandmarks:
            x1, y1, z1 = self.joints[landmark1][0] - fingerXYZ[0], self.joints[landmark1][1] - fingerXYZ[1], self.joints[landmark1][2] - fingerXYZ[2]
            x2, y2, z2 = self.joints[landmark2][0] - fingerXYZ[0], self.joints[landmark2][1] - fingerXYZ[1], self.joints[landmark2][2] - fingerXYZ[2]
            # 3D
            #angle = math.acos((x1*x2 + y1*y2 + z1*z2) / ((x1**2 + y1**2 + z1**2) ** 0.5 * (x2**2 + y2**2 + z2**2) ** 0.5))
            # 2D
            try:
                angle = math.acos((x1*x2 + y1*y2) / ((x1**2 + y1**2) ** 0.5 * (x2**2 + y2**2) ** 0.5))
            except:
                angle = 0
            angles[(landmark1, landmark2)] = angle

        return angles

    def calculateNearestFingerNodeByNearestNearestAlgorithm(self, targetXYZ):
        jointLandmarks = [i for i in range(5, 21)] 
        distanceFromJoints = self.calculateDistanceFromJoints(targetXYZ, jointLandmarks)

        # NearestJoint
        nearestJointLandmark = [k for k,v in distanceFromJoints.items() if min(distanceFromJoints.values()) == v][0]

        # NearestJoint of NearestJoint
        fingerOfNearestJoint = [k for k,v in self.landmarksInfo.items() if nearestJointLandmark in v][0]
        distanceFromJointsOfNearJoints = {landmark: distanceFromJoints[landmark] for landmark in [nearestJointLandmark-1, nearestJointLandmark+1] if landmark in self.landmarksInfo[fingerOfNearestJoint]}
        nearestJointLandmarkOfNearestJoint = [k for k, v in distanceFromJointsOfNearJoints.items() if min(distanceFromJointsOfNearJoints.values()) == v][0]

        # NearestNode
        vertexsOfNearestNode = [nearestJointLandmark, nearestJointLandmarkOfNearestJoint]
        vertexsOfNearestNode.sort()

        nearestNode = self.landmarksInfo[fingerOfNearestJoint][0]//4, self.landmarksInfo[fingerOfNearestJoint].index(vertexsOfNearestNode[0]) # 3, 3 (middleFinger, third)

        return nearestNode


    def calculateDistanceFromJoints(self, fingerXYZ, jointLandmarks):
        distanceFromJoints = {}

        for jointLandmark in jointLandmarks:
            jointXYZ = self.joints[jointLandmark]
            #distance = ((fingerXYZ[0]-jointXYZ[0]) ** 2 + (fingerXYZ[1]-jointXYZ[1]) ** 2) ** 0.5
            distance = ((fingerXYZ[0]-jointXYZ[0]) ** 2 + (fingerXYZ[1]-jointXYZ[1]) ** 2 + (fingerXYZ[2]-jointXYZ[2]) ** 2) ** 0.5
            distanceFromJoints[jointLandmark] = distance
        
        return distanceFromJoints


    def getJoints(self):
        jointsArray = np.empty((0, 3), float)

        for landmark in self.landmarks:
            jointsArray = np.append(jointsArray, np.array([self.joints[landmark]]), axis=0)

        return jointsArray


    def getPinkyEdge(self):
        return (self.joints[0][:2], self.joints[20][:2])

    def getIndexEdge(self):
        return (self.joints[1][:2], self.joints[8][:2])

    def getUpperEdge(self):
        return (self.joints[8][:2], self.joints[20][:2])


