# simplified_gui.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from pose_estimation import PoseEstimator
from angle_calculator import calculate_angle
from exercise_counter import SquatCounter
from gamification import Gamification
from database import ProgressTracker

import pyttsx3
import cv2
import numpy as np

class RehabAppSimple(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple Knee Rehabilitation App')
        self.setGeometry(100, 100, 800, 600)

        # Initialize Text-to-Speech
        self.engine = pyttsx3.init()
        self.last_feedback = ""

        # Initialize Progress Tracker
        self.progress_tracker = ProgressTracker()

        # Create Widgets
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet("background-color: black;")

        self.start_button = QPushButton('Start Exercise')
        self.stop_button = QPushButton('Stop Exercise')
        self.stop_button.setEnabled(False)

        self.counter_label = QLabel('Repetitions: 0')
        self.feedback_label = QLabel('Feedback: Ready')
        self.points_label = QLabel('Points: 0')
        self.achievements_label = QLabel('Achievements: None')

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.counter_label)
        stats_layout.addWidget(self.feedback_label)
        stats_layout.addWidget(self.points_label)
        stats_layout.addWidget(self.achievements_label)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(stats_layout)

        self.setLayout(main_layout)

        # Initialize Pose Estimator and Counters
        self.pose_estimator = PoseEstimator()
        self.squat_counter = SquatCounter()
        self.gamification = Gamification()

        # Connect Buttons
        self.start_button.clicked.connect(self.start_exercise)
        self.stop_button.clicked.connect(self.stop_exercise)

        # Timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def start_exercise(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start(30)  # ~33 FPS

    def stop_exercise(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()

        # Record progress
        reps = int(self.counter_label.text().split(": ")[1])
        points = int(self.points_label.text().split(": ")[1])
        self.progress_tracker.record_progress(reps, points)

        # Reset counters
        self.counter_label.setText('Repetitions: 0')
        self.feedback_label.setText('Feedback: Ready')
        self.points_label.setText('Points: 0')
        self.achievements_label.setText('Achievements: None')

    def update_frame(self):
        ret, frame = cv2.VideoCapture(0).read()
        if not ret:
            return

        frame = cv2.resize(frame, (800, 600))
        image, results = self.pose_estimator.process_frame(frame)
        image = self.pose_estimator.draw_landmarks(image, results)
        landmarks = self.pose_estimator.get_landmarks(results)

        if landmarks:
            try:
                left_hip = [
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_HIP.value].y
                ]
                left_knee = [
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_KNEE.value].y
                ]
                left_ankle = [
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                    landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_ANKLE.value].y
                ]

                angle = calculate_angle(left_hip, left_knee, left_ankle)
                reps, feedback = self.squat_counter.update(angle)

                # Update labels
                self.counter_label.setText(f"Repetitions: {reps}")
                self.feedback_label.setText(f"Feedback: {feedback}")
                self.gamification.add_points(1)
                self.points_label.setText(f"Points: {self.gamification.get_points()}")

                # Check for achievements
                achievements = self.gamification.get_achievements()
                if achievements:
                    self.achievements_label.setText(f"Achievements: {', '.join(achievements)}")

                # Audio feedback
                if feedback != self.last_feedback:
                    self.engine.say(feedback)
                    self.engine.runAndWait()
                    self.last_feedback = feedback

                # Annotate angle
                h, w, _ = frame.shape
                knee_coords = (int(left_knee[0] * w), int(left_knee[1] * h))
                color = (0, 255, 0)  # Default color
                if feedback == "Too Low!":
                    color = (0, 0, 255)  # Red
                elif feedback == "Good Rep":
                    color = (0, 255, 0)  # Green
                else:
                    color = (255, 255, 0)  # Yellow

                cv2.putText(image, f"{int(angle)}°", knee_coords, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

            except Exception as e:
                print(f"Error: {e}")

        # Convert image to QImage
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
        self.video_label.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        self.progress_tracker.close()
        self.engine.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RehabAppSimple()
    window.show()
    sys.exit(app.exec_())
