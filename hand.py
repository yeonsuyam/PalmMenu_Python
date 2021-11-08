class Hand():
    def __init__(self, handInfo, landmarks):
        self.handInfo = handInfo # Right | Left
        self.landmarks = landmarks
        self.joints = [[0, 0, 0] for i in range(len(landmarks))]

        
    def updateHandJoints(self, handLandmarks):
        for i, landmark in enumerate(self.landmarks):
            self.joints[i][0] = handLandmarks.landmark[landmark].x
            self.joints[i][1] = handLandmarks.landmark[landmark].y
            self.joints[i][2] = handLandmarks.landmark[landmark].z
        
        print(self.joints)
