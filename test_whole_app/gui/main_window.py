# gui/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QComboBox, QSpinBox, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

import cv2
import sys

from test_whole_app.modules.pose_estimation import PoseEstimator
from test_whole_app.modules.exercises.knee_exercise import KneeExercise
from test_whole_app.modules.exercises.shoulder_exercise import ShoulderExercise
from test_whole_app.modules.exercises.back_exercise import BackExercise
from test_whole_app.modules.exercises.squat_exercise import SquatExercise
from test_whole_app.modules.database import ProgressTracker
from test_whole_app.utils.helper_functions import convert_cv_qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rehabilitation Exercise App")
        self.setGeometry(100, 100, 1300, 800)

        # Initialize Pose Estimator
        self.pose_estimator = PoseEstimator()

        # Initialize Exercise Modules
        self.exercises = {
            "Knee Exercise": KneeExercise(),
            "Shoulder Exercise": ShoulderExercise(),
            "Back Exercise": BackExercise(),
            "Squat Exercise": SquatExercise()
        }
        self.current_exercise = "Knee Exercise"

        # Initialize Progress Tracker
        self.progress_tracker = ProgressTracker()

        # Setup UI Components
        self.setup_ui()

        # Initialize Video Capture
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Cannot open webcam.")
            sys.exit()

        # Setup Timer for Video Capture
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms

    def setup_ui(self):
        """
        Setup the main UI components.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Top Layout for Controls
        controls_layout = QHBoxLayout()

        # Exercise Selection
        self.exercise_label = QLabel("Exercise:")
        self.exercise_label.setFont(QFont("Arial", 12))
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(self.exercises.keys())
        self.exercise_combo.currentTextChanged.connect(self.change_exercise)

        # Goal Setting
        self.goal_label = QLabel("Set Goal (Reps):")
        self.goal_label.setFont(QFont("Arial", 12))
        self.goal_spinbox = QSpinBox()
        self.goal_spinbox.setRange(1, 1000)
        self.goal_spinbox.setValue(20)  # Default goal

        # Start/Stop Button
        self.start_button = QPushButton("Start Exercise")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.toggle_exercise)

        # Add widgets to controls layout
        controls_layout.addWidget(self.exercise_label)
        controls_layout.addWidget(self.exercise_combo)
        controls_layout.addWidget(self.goal_label)
        controls_layout.addWidget(self.goal_spinbox)
        controls_layout.addWidget(self.start_button)

        # Feedback Label
        self.feedback_label = QLabel("Feedback: Ready")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setFont(QFont("Arial", 14))
        self.feedback_label.setStyleSheet("color: blue;")

        # Repetitions and Points
        reps_points_layout = QHBoxLayout()

        self.reps_label = QLabel("Repetitions: 0")
        self.reps_label.setFont(QFont("Arial", 12))
        self.points_label = QLabel("Points: 0")
        self.points_label.setFont(QFont("Arial", 12))

        reps_points_layout.addWidget(self.reps_label)
        reps_points_layout.addWidget(self.points_label)

        # Achievement Label
        self.achievement_label = QLabel("Achievements: None")
        self.achievement_label.setAlignment(Qt.AlignCenter)
        self.achievement_label.setFont(QFont("Arial", 12))
        self.achievement_label.setStyleSheet("color: green;")

        # Video Display
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)  # Increased size
        self.video_label.setStyleSheet("border: 2px solid #555;")
        self.video_label.setAlignment(Qt.AlignCenter)

        # Add all to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.feedback_label)
        main_layout.addLayout(reps_points_layout)
        main_layout.addWidget(self.achievement_label)
        main_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        central_widget.setLayout(main_layout)

    def change_exercise(self, exercise_name):
        """
        Change the current exercise based on user selection.
        """
        self.current_exercise = exercise_name
        self.reset_metrics()

    def toggle_exercise(self):
        """
        Start or stop the exercise.
        """
        if self.start_button.text() == "Start Exercise":
            self.start_button.setText("Stop Exercise")
            self.current_goal = self.goal_spinbox.value()
            self.reset_metrics()
        else:
            self.start_button.setText("Start Exercise")
            self.reset_metrics()

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

    def update_frame(self):
        """
        Capture video frame, process it, and update the GUI.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        frame = cv2.flip(frame, 1)  # Mirror the image
        frame = cv2.resize(frame, (1100, 900))  # Match video_label size
        image, results = self.pose_estimator.process_frame(frame)
        image = self.pose_estimator.draw_landmarks(image, results, exercise=self.current_exercise, focus_side='right')

        if self.start_button.text() == "Stop Exercise":
            relevant_landmarks = self.pose_estimator.get_relevant_landmarks(results, exercise=self.current_exercise, focus_side='right')
            if relevant_landmarks:
                exercise_module = self.exercises[self.current_exercise]
                try:
                    reps, feedback, points, achievements = exercise_module.process(relevant_landmarks)
                except KeyError as e:
                    print(f"Error processing exercise: {e}")
                    reps, feedback, points, achievements = self.reps, "Error", self.points, []

                self.reps = reps
                self.feedback = feedback
                self.reps_label.setText(f"Repetitions: {self.reps}")
                self.feedback_label.setText(f"Feedback: {self.feedback}")

                if feedback == "Good Rep":
                    self.points = points
                    self.points_label.setText(f"Points: {self.points}")
                    if achievements:
                        achievement_text = ", ".join(achievements)
                        self.achievement_label.setText(f"Achievements: {achievement_text}")
                        # QMessageBox.information(self, "Achievement Unlocked", f"{achievements[-1]}")

                # Check if goal is reached
                if self.reps >= self.current_goal:
                    QMessageBox.information(self, "Goal Reached", f"Congratulations! You reached your goal of {self.current_goal} reps.")
                    self.start_button.setText("Start Exercise")
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
