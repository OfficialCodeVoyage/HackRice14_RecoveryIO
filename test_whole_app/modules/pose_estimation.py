# modules/pose_estimation.py
import os

import cv2
import mediapipe as mp
from PyQt5 import Qt
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QLabel

from test_whole_app.utils.helper_functions import convert_cv_qt


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

    def get_relevant_landmarks(self, results, exercise, focus_side):
        """
        Extract relevant landmarks based on the exercise.

        Parameters:
        - results: Pose estimation results.
        - exercise (str): Current exercise name.
        - focus_side (str): 'left' or 'right'.

        Returns:
        - landmarks (dict): Relevant landmarks with their coordinates.
        """
        if not results.pose_landmarks:
            return None

        landmarks = {}
        pose_landmarks = results.pose_landmarks.landmark

        try:
            if exercise in ["Knee Exercise", "Squat Exercise"]:
                side = focus_side.lower()
                landmarks['hip'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_HIP"].value].x,
                                    pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_HIP"].value].y]
                landmarks['knee'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_KNEE"].value].x,
                                     pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_KNEE"].value].y]
                landmarks['ankle'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_ANKLE"].value].x,
                                      pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_ANKLE"].value].y]
            elif exercise == "Shoulder Exercise":
                side = focus_side.lower()
                landmarks['shoulder'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_SHOULDER"].value].x,
                                          pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_SHOULDER"].value].y]
                landmarks['elbow'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_ELBOW"].value].x,
                                       pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_ELBOW"].value].y]
                landmarks['wrist'] = [pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_WRIST"].value].x,
                                       pose_landmarks[self.mp_pose.PoseLandmark[f"{side.upper()}_WRIST"].value].y]
            elif exercise == "Back Exercise":
                landmarks['left_shoulder'] = [pose_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                              pose_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                landmarks['right_shoulder'] = [pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                               pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                landmarks['left_hip'] = [pose_landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                         pose_landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                landmarks['right_hip'] = [pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                          pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            else:
                # Unsupported exercise
                return None
        except IndexError as e:
            print(f"Landmark index error: {e}")
            return None

        return landmarks

    def toggle_exercise(self):
        """
        Start or stop the exercise.
        """
        if self.start_button.text() == "Start Exercise":
            self.start_button.setText("Stop Exercise")
            self.start_button.setIcon(QIcon(os.path.join('assets', 'icons', 'stop.png')))
            self.current_goal = self.goal_spinbox.value()
            self.reset_metrics()
            self.progress_bar.setMaximum(self.current_goal)
            self.progress_bar.setValue(0)
            self.status_bar.showMessage(f"Exercise '{self.current_exercise}' started. Aim for {self.current_goal} reps.")
        else:
            self.start_button.setText("Start Exercise")
            self.start_button.setIcon(QIcon(os.path.join('assets', 'icons', 'start.png')))
            self.reset_metrics()
            self.status_bar.showMessage("Exercise stopped.")

    def reset_metrics(self):
        """
        Reset the repetitions, points, and feedback.
        """
        self.reps = 0
        self.points = 0
        self.feedback = "Ready"
        self.feedback_label.setText(f"Feedback: {self.feedback}")
        self.reps_label.setText(f"Repetitions: {self.reps}")
        self.points_label.setText(f"Points: {self.points}")
        self.achievement_label.setText("Achievements: None")
        self.knee_angle_label.setText("Knee Angle: --°")
        self.back_angle_label.setText("Back Angle: --°")
        self.shoulder_angle_label.setText("Shoulder Angle: --°")
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Metrics reset.")

    def view_tutorial(self):
        """
        Display the tutorial GIF for the selected exercise.
        """
        tutorial_filename = f"{self.current_exercise.lower().replace(' ', '_')}_exercise.gif"
        tutorial_path = os.path.join('assets', 'tutorials', tutorial_filename)
        if not os.path.exists(tutorial_path):
            QMessageBox.warning(self, "Tutorial Not Found", "Tutorial for this exercise is not available.")
            return

        # Create a new window to display the tutorial
        self.tutorial_window = QWidget()
        self.tutorial_window.setWindowTitle(f"{self.current_exercise} Tutorial")
        self.tutorial_window.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()
        self.tutorial_label = QLabel()
        self.tutorial_label.setAlignment(Qt.AlignCenter)

        # Load and set the GIF
        movie = QMovie(tutorial_path)
        self.tutorial_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.tutorial_label)
        self.tutorial_window.setLayout(layout)
        self.tutorial_window.show()

    def update_frame(self):
        """
        Capture video frame, process it, and update the GUI.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        frame = cv2.flip(frame, 1)  # Mirror the image
        frame = cv2.resize(frame, (800, 600))  # Adjusted size to match video_label
        image, results = self.pose_estimator.process_frame(frame)
        image = self.pose_estimator.draw_landmarks(image, results, exercise=self.current_exercise, focus_side='right')

        if self.start_button.text() == "Stop Exercise":
            relevant_landmarks = self.pose_estimator.get_relevant_landmarks(results, exercise=self.current_exercise, focus_side='right')
            if relevant_landmarks:
                exercise_module = self.exercises[self.current_exercise]
                try:
                    if self.current_exercise == "Squat Exercise":
                        reps, feedback, points, achievements, knee_angle, back_angle = exercise_module.process(relevant_landmarks)
                        shoulder_angle = None
                    elif self.current_exercise == "Back Exercise":
                        reps, feedback, points, achievements, back_angle = exercise_module.process(relevant_landmarks)
                        knee_angle = None
                        shoulder_angle = None
                    elif self.current_exercise == "Shoulder Exercise":
                        reps, feedback, points, achievements, shoulder_angle = exercise_module.process(relevant_landmarks)
                        knee_angle = None
                        back_angle = None
                    else:  # Knee Exercise
                        reps, feedback, points, achievements, knee_angle = exercise_module.process(relevant_landmarks)
                        back_angle = None
                        shoulder_angle = None
                except KeyError as e:
                    print(f"Error processing exercise: {e}")
                    reps, feedback, points, achievements = self.reps, "Error", self.points, []
                    knee_angle, back_angle, shoulder_angle = None, None, None

                # Update metrics
                self.reps = reps
                self.feedback = feedback
                self.reps_label.setText(f"Repetitions: {self.reps}")
                self.points_label.setText(f"Points: {self.points}")
                self.feedback_label.setText(f"Feedback: {self.feedback}")

                # Update angles display
                if knee_angle is not None:
                    self.knee_angle_label.setText(f"Knee Angle: {int(knee_angle)}°")
                else:
                    self.knee_angle_label.setText("Knee Angle: --°")

                if back_angle is not None:
                    self.back_angle_label.setText(f"Back Angle: {int(back_angle)}°")
                else:
                    self.back_angle_label.setText("Back Angle: --°")

                if self.current_exercise == "Shoulder Exercise" and shoulder_angle is not None:
                    self.shoulder_angle_label.setText(f"Shoulder Angle: {int(shoulder_angle)}°")
                else:
                    self.shoulder_angle_label.setText("Shoulder Angle: --°")

                # Update Progress Bar
                self.progress_bar.setValue(self.reps)

                # Change feedback label color based on feedback
                if feedback == "Good Rep":
                    self.feedback_label.setStyleSheet("color: green;")
                elif feedback == "Keep Your Back Straight":
                    self.feedback_label.setStyleSheet("color: red;")
                elif feedback == "Go Up":
                    self.feedback_label.setStyleSheet("color: orange;")
                else:
                    self.feedback_label.setStyleSheet("color: blue;")

                # Handle Achievements (No Pop-ups)
                if feedback == "Good Rep":
                    if achievements:
                        achievement_text = ", ".join(achievements)
                        self.achievement_label.setText(f"Achievements: {achievement_text}")
                        self.status_bar.showMessage(f"Achievement Unlocked: {achievements[-1]}")

                # Check if goal is reached
                if self.reps >= self.current_goal:
                    QMessageBox.information(self, "Goal Reached", f"Congratulations! You reached your goal of {self.current_goal} reps.")
                    self.start_button.setText("Start Exercise")
                    self.start_button.setIcon(QIcon(os.path.join('assets', 'icons', 'start.png')))
                    self.status_bar.showMessage(f"Goal reached: {self.current_goal} reps.")
                    # Record progress
                    self.progress_tracker.record_progress(self.current_exercise, self.reps, self.points)
                    self.reset_metrics()

        # Convert the image to Qt format
        try:
            qt_image = convert_cv_qt(image)
            self.video_label.setPixmap(qt_image)
        except Exception as e:
            print(f"Error converting image: {e}")

    def closeEvent(self, event):
        """
        Handle the window close event to release resources.
        """
        self.cap.release()
        self.pose_estimator.close()
        self.progress_tracker.close()
        event.accept()
