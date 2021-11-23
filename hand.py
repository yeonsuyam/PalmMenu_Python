class Hand():
    def __init__(self, handInfo, landmarks=[i for i in range(21)]):
        self.handInfo = handInfo # Right | Left
        self.landmarks = landmarks
        self.joints = {i: [0, 0, 0] for i in landmarks}
        self.landmarksInfo = {"thumbs": [i for i in range(1, 5)], 
                                "index": [i for i in range(5, 9)], 
                                "middle": [i for i in range(9, 13)], 
                                "ring": [i for i in range(13, 17)], 
                                "pinky": [i for i in range(17, 21)]}
        
    def updateHandJoints(self, handLandmarks):
        for landmark in self.landmarks:
            self.joints[landmark][0] = handLandmarks.landmark[landmark].x
            self.joints[landmark][1] = handLandmarks.landmark[landmark].y
            self.joints[landmark][2] = handLandmarks.landmark[landmark].z
        
        #print(self.joints)

    def getFingerXYZ(self, landmarkNum):
        return self.joints[landmarkNum]


    def calculateNearestFingerNode(self, targetXYZ):
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

        #print("fingerOfNearestJoint: ", fingerOfNearestJoint) # ring
        #print("vertexsOfNearestNode: ", vertexsOfNearestNode) # [15, 16]
        #print("landmarksInfo: ", self.landmarksInfo[fingerOfNearestJoint]) # [13, 14, 15, 16]
        nearestNode = self.landmarksInfo[fingerOfNearestJoint][0]//4, self.landmarksInfo[fingerOfNearestJoint].index(vertexsOfNearestNode[0]) # 3, 3 (middleFinger, third)

        return nearestNode


    def calculateDistanceFromJoints(self, fingerXYZ, jointLandmarks):
        distanceFromJoints = {}

        for jointLandmark in jointLandmarks:
            jointXYZ = self.joints[jointLandmark]
            distance = ((fingerXYZ[0]-jointXYZ[0]) ** 2 + (fingerXYZ[1]-jointXYZ[1]) ** 2) ** 0.5
            distanceFromJoints[jointLandmark] = distance
        
        return distanceFromJoints
