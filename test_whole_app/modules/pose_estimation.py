# modules/pose_estimation.py

import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the PoseEstimator with MediaPipe's Pose solution.

        Parameters:
        - min_detection_confidence (float): Minimum confidence value ([0.0, 1.0]) for pose detection.
        - min_tracking_confidence (float): Minimum confidence value ([0.0, 1.0]) for pose tracking.
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_frame(self, frame):
        """
        Process a video frame for pose estimation.

        Parameters:
        - frame (numpy.ndarray): The current video frame.

        Returns:
        - image (numpy.ndarray): The processed image with pose landmarks.
        - results (mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList): Pose estimation results.
        """
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results

    def get_relevant_landmarks(self, results, exercise='Knee Exercise', focus_side='right'):
        """
        Extract relevant landmarks based on the current exercise.

        Parameters:
        - results: MediaPipe pose estimation results.
        - exercise (str): Current exercise name.
        - focus_side (str): 'left' or 'right' to specify the side.

        Returns:
        - dict or None: Contains the necessary landmarks for the exercise.
        """
        if not results.pose_landmarks:
            return None

        landmarks = results.pose_landmarks.landmark
        relevant_landmarks = {}

        try:
            if exercise in ["Knee Exercise", "Squat Exercise"]:
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
            elif exercise == "Shoulder Exercise":
                if focus_side.lower() == 'left':
                    relevant_landmarks['shoulder'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                                     landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    relevant_landmarks['elbow'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                                  landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    relevant_landmarks['wrist'] = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                                  landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                else:
                    relevant_landmarks['shoulder'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                                     landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    relevant_landmarks['elbow'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    relevant_landmarks['wrist'] = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                                  landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            elif exercise == "Back Exercise":
                # Calculate midpoints for upper_back and lower_back
                upper_back_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x +
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) / 2
                upper_back_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
                lower_back_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x +
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2
                lower_back_y = (landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
                hips_x = lower_back_x
                hips_y = lower_back_y

                relevant_landmarks['upper_back'] = [upper_back_x, upper_back_y]
                relevant_landmarks['lower_back'] = [lower_back_x, lower_back_y]
                relevant_landmarks['hips'] = [hips_x, hips_y]
            else:
                # Unsupported exercise
                return None

            return relevant_landmarks
        except IndexError as e:
            # Handle cases where landmarks are not detected
            print(f"Landmark extraction error: {e}")
            return None

    def draw_landmarks(self, image, results, exercise='Knee Exercise', focus_side='right'):
        """
        Draw pose landmarks on the image, focusing only on the specified exercise.

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
                connections,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            # Add visual indicators for Squat Exercise to maintain straight back
            if exercise == "Squat Exercise":
                # Draw circles on upper_back and lower_back
                upper_back = [
                    (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x +
                     results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x) / 2,
                    (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y +
                     results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
                ]
                lower_back = [
                    (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].x +
                     results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2,
                    (results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].y +
                     results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2
                ]

                # Convert normalized coordinates to pixel values
                h, w, _ = image.shape
                upper_back_pixel = (int(upper_back[0] * w), int(upper_back[1] * h))
                lower_back_pixel = (int(lower_back[0] * w), int(lower_back[1] * h))

                # Draw circles
                cv2.circle(image, upper_back_pixel, 10, (0, 255, 0), -1)  # Green dot
                cv2.circle(image, lower_back_pixel, 10, (0, 255, 0), -1)  # Green dot

                # Draw dotted line between upper_back and lower_back
                self.draw_dotted_line(image, upper_back_pixel, lower_back_pixel, color=(0, 255, 0), thickness=2, gap=10)

        def draw_dotted_line(self, img, pt1, pt2, color, thickness=1, gap=10):
            """
            Draw a dotted line between two points.

            Parameters:
            - img (numpy.ndarray): The image to draw on.
            - pt1 (tuple): Starting point (x, y).
            - pt2 (tuple): Ending point (x, y).
            - color (tuple): BGR color.
            - thickness (int): Thickness of the line.
            - gap (int): Gap between dots.
            """
            dist = ((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2) ** 0.5
            pts = []
            for i in range(0, int(dist), gap):
                r = i / dist
                x = int((pt2[0] - pt1[0]) * r + pt1[0])
                y = int((pt2[1] - pt1[1]) * r + pt1[1])
                pts.append((x, y))
            for point in pts:
                cv2.circle(img, point, thickness, color, -1)

    def close(self):
        """
        Close the MediaPipe Pose instance.
        """
        self.pose.close()
