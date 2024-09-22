# pose_estimation.py
import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results

    def get_relevant_landmarks(self, results, focus_side='right'):
        """
        Extracts only the hip, knee, and ankle landmarks for the specified side.

        Parameters:
        - results: MediaPipe pose estimation results.
        - focus_side (str): 'left' or 'right' to specify which knee to focus on.

        Returns:
        - dict: Contains the x and y coordinates of hip, knee, and ankle.
        """
        if not results.pose_landmarks:
            return None

        landmarks = results.pose_landmarks.landmark
        relevant_landmarks = {}

        try:
            if focus_side.lower() == 'left':
                relevant_landmarks['hip'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                             landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                relevant_landmarks['knee'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                              landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                relevant_landmarks['ankle'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                               landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            else:
                relevant_landmarks['hip'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                             landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                relevant_landmarks['knee'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                              landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                relevant_landmarks['ankle'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                               landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            return relevant_landmarks
        except IndexError as e:
            # Handle cases where landmarks are not detected
            print(f"Landmark extraction error: {e}")
            return None

    def close(self):
        self.pose.close()
