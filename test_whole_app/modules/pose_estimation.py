# modules/pose_estimation.py

import cv2
import mediapipe as mp

class PoseEstimator:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=min_detection_confidence,
                                      min_tracking_confidence=min_tracking_confidence)
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame):
        """
        Process the frame for pose estimation.

        Parameters:
        - frame (numpy.ndarray): The image frame to process.

        Returns:
        - image (numpy.ndarray): The image with pose landmarks drawn.
        - results (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Pose estimation results.
        """
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results

    def draw_landmarks(self, image, results, exercise, focus_side):
        """
        Draw pose landmarks on the image based on the exercise.

        Parameters:
        - image (numpy.ndarray): The image to draw landmarks on.
        - results (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Pose estimation results.
        - exercise (str): Current exercise name.
        - focus_side (str): 'left' or 'right' to specify the side.

        Returns:
        - image (numpy.ndarray): The image with drawn landmarks.
        """
        if results.pose_landmarks:
            # Define connections based on exercise
            connections = []
            if exercise in ["Knee Exercise", "Squat Exercise"]:
                if focus_side.lower() == 'left':
                    connections = [
                        (self.mp_pose.PoseLandmark.LEFT_HIP.value, self.mp_pose.PoseLandmark.LEFT_KNEE.value),
                        (self.mp_pose.PoseLandmark.LEFT_KNEE.value, self.mp_pose.PoseLandmark.LEFT_ANKLE.value)
                    ]
                else:
                    connections = [
                        (self.mp_pose.PoseLandmark.RIGHT_HIP.value, self.mp_pose.PoseLandmark.RIGHT_KNEE.value),
                        (self.mp_pose.PoseLandmark.RIGHT_KNEE.value, self.mp_pose.PoseLandmark.RIGHT_ANKLE.value)
                    ]
            elif exercise == "Shoulder Exercise":
                if focus_side.lower() == 'left':
                    connections = [
                        (self.mp_pose.PoseLandmark.LEFT_SHOULDER.value, self.mp_pose.PoseLandmark.LEFT_ELBOW.value),
                        (self.mp_pose.PoseLandmark.LEFT_ELBOW.value, self.mp_pose.PoseLandmark.LEFT_WRIST.value)
                    ]
                else:
                    connections = [
                        (self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value, self.mp_pose.PoseLandmark.RIGHT_ELBOW.value),
                        (self.mp_pose.PoseLandmark.RIGHT_ELBOW.value, self.mp_pose.PoseLandmark.RIGHT_WRIST.value)
                    ]
            elif exercise == "Back Exercise":
                connections = [
                    (self.mp_pose.PoseLandmark.LEFT_SHOULDER.value, self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
                    (self.mp_pose.PoseLandmark.LEFT_HIP.value, self.mp_pose.PoseLandmark.RIGHT_HIP.value)
                ]
            else:
                # Unsupported exercise
                return image

            # Draw the landmarks
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

        return image

    def close(self):
        """
        Close the MediaPipe Pose instance.
        """
        self.pose.close()
