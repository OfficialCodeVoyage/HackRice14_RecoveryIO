# gui/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QComboBox, QSpinBox, QMessageBox, QHBoxLayout, QProgressBar, QTextEdit, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor, QMovie

import cv2
import sys
import os

from test_whole_app.modules.angle_calculator import calculate_angle
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
        self.setGeometry(100, 100, 1300, 900)  # Updated window size

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

        main_layout = QHBoxLayout()  # Split into left and right columns

        # Left Column Layout for Video and Tutorial
        left_layout = QVBoxLayout()

        # Video Display
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)  # Adjusted size
        self.video_label.setStyleSheet("border: 2px solid #555;")
        self.video_label.setAlignment(Qt.AlignCenter)

        # Tutorial Button
        self.tutorial_button = QPushButton("View Tutorial")
        self.tutorial_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.tutorial_button.clicked.connect(self.view_tutorial)

        left_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.tutorial_button, alignment=Qt.AlignCenter)

        # Right Column Layout for Controls and Instructions
        right_layout = QVBoxLayout()

        # Top Controls Layout
        controls_layout = QHBoxLayout()

        # Exercise Selection
        self.exercise_label = QLabel("Exercise:")
        self.exercise_label.setFont(QFont("Arial", 14))
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(self.exercises.keys())
        self.exercise_combo.currentTextChanged.connect(self.change_exercise)

        # Goal Setting
        self.goal_label = QLabel("Set Goal (Reps):")
        self.goal_label.setFont(QFont("Arial", 14))
        self.goal_spinbox = QSpinBox()
        self.goal_spinbox.setRange(1, 1000)
        self.goal_spinbox.setValue(20)  # Default goal

        # Start/Stop Button
        self.start_button = QPushButton("Start Exercise")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
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
        self.feedback_label.setFont(QFont("Arial", 16))
        self.feedback_label.setStyleSheet("color: blue;")

        # Real-time Angle Display
        angles_layout = QHBoxLayout()

        self.knee_angle_label = QLabel("Knee Angle: --°")
        self.knee_angle_label.setFont(QFont("Arial", 14))
        self.knee_angle_label.setStyleSheet("color: black;")

        self.back_angle_label = QLabel("Back Angle: --°")
        self.back_angle_label.setFont(QFont("Arial", 14))
        self.back_angle_label.setStyleSheet("color: black;")

        angles_layout.addWidget(self.knee_angle_label)
        angles_layout.addWidget(self.back_angle_label)

        # Repetitions and Points
        reps_points_layout = QHBoxLayout()

        self.reps_label = QLabel("Repetitions: 0")
        self.reps_label.setFont(QFont("Arial", 14))
        self.points_label = QLabel("Points: 0")
        self.points_label.setFont(QFont("Arial", 14))

        reps_points_layout.addWidget(self.reps_label)
        reps_points_layout.addWidget(self.points_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat("Progress: %p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)

        # Achievement Label
        self.achievement_label = QLabel("Achievements: None")
        self.achievement_label.setAlignment(Qt.AlignCenter)
        self.achievement_label.setFont(QFont("Arial", 12))
        self.achievement_label.setStyleSheet("color: green;")

        # Instructions Panel
        self.instructions_label = QLabel("Instructions:")
        self.instructions_label.setFont(QFont("Arial", 14))
        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        self.instructions_text.setFont(QFont("Arial", 12))
        self.instructions_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
        """)
        self.set_instructions("Knee Exercise", """
- **Stand upright** with feet shoulder-width apart.
- **Bend your knees** to lower your body as if sitting back into a chair.
- **Keep your back straight** and chest up.
- **Lower until your thighs are parallel** to the ground.
- **Push through your heels** to return to the starting position.
""")

        # Add widgets to right layout
        right_layout.addLayout(controls_layout)
        right_layout.addWidget(self.feedback_label)
        right_layout.addLayout(angles_layout)
        right_layout.addLayout(reps_points_layout)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.achievement_label)
        right_layout.addWidget(self.instructions_label)
        right_layout.addWidget(self.instructions_text)

        # Add left and right layouts to main layout
        main_layout.addLayout(left_layout, stretch=2)  # Video and Tutorial
        main_layout.addLayout(right_layout, stretch=1)  # Controls and Instructions

        central_widget.setLayout(main_layout)

    def set_instructions(self, exercise, instructions):
        """
        Set instructions based on the selected exercise.

        Parameters:
        - exercise (str): Current exercise name.
        - instructions (str): Instruction text.
        """
        self.instructions_text.setText(instructions)

    def change_exercise(self, exercise_name):
        """
        Change the current exercise based on user selection.
        """
        self.current_exercise = exercise_name
        self.reset_metrics()
        # Update instructions based on exercise
        instructions = self.get_instructions(exercise_name)
        self.set_instructions(exercise_name, instructions)

    def get_instructions(self, exercise_name):
        """
        Retrieve instructions based on the exercise name.

        Parameters:
        - exercise_name (str): Name of the exercise.

        Returns:
        - instructions (str): Instruction text.
        """
        instructions_dict = {
            "Knee Exercise": """
- **Stand upright** with feet shoulder-width apart.
- **Bend your knees** to lower your body as if sitting back into a chair.
- **Keep your back straight** and chest up.
- **Lower until your thighs are parallel** to the ground.
- **Push through your heels** to return to the starting position.
""",
            "Shoulder Exercise": """
- **Stand or sit upright** with your back straight.
- **Extend your arms out** to the sides at shoulder height.
- **Slowly raise your arms** above your head, keeping them straight.
- **Hold for a moment** at the top.
- **Lower your arms** back to the starting position.
- **Repeat** for the desired number of repetitions.
""",
            "Back Exercise": """
- **Stand sideways** to the camera for optimal back alignment.
- **Place your hands** on your hips.
- **Slowly bend forward** at the hips, keeping your back straight.
- **Lower your torso** until it's nearly parallel to the ground.
- **Hold for a few seconds**.
- **Return to the starting position** by contracting your back muscles.
- **Repeat** for the desired number of repetitions.
""",
            "Squat Exercise": """
- **Stand sideways** to the camera with feet shoulder-width apart.
- **Bend your knees** to lower your body as if sitting back into a chair.
- **Keep your back straight** and chest up. Focus on the dots on your back to maintain alignment.
- **Lower until your thighs are parallel** to the ground.
- **Push through your heels** to return to the starting position.
- **Repeat** for the desired number of repetitions.
""",
        }
        return instructions_dict.get(exercise_name, "No instructions available.")

    def toggle_exercise(self):
        """
        Start or stop the exercise.
        """
        if self.start_button.text() == "Start Exercise":
            self.start_button.setText("Stop Exercise")
            self.current_goal = self.goal_spinbox.value()
            self.reset_metrics()
            self.progress_bar.setMaximum(self.current_goal)
            self.progress_bar.setValue(0)
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
        self.knee_angle_label.setText("Knee Angle: --°")
        self.back_angle_label.setText("Back Angle: --°")
        self.progress_bar.setValue(0)

    def view_tutorial(self):
        """
        Display the tutorial GIF for the selected exercise.
        """
        tutorial_path = os.path.join('tutorials', f"{self.current_exercise.lower().replace(' ', '_')}_exercise.gif")
        if not os.path.exists(tutorial_path):
            QMessageBox.warning(self, "Tutorial Not Found", "Tutorial for this exercise is not available.")
            return

        # Create a new window to display the tutorial
        self.tutorial_window = QWidget()
        self.tutorial_window.setWindowTitle(f"{self.current_exercise} Tutorial")
        self.tutorial_window.setGeometry(150, 150, 600, 400)

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
                    reps, feedback, points, achievements = exercise_module.process(relevant_landmarks)
                except KeyError as e:
                    print(f"Error processing exercise: {e}")
                    reps, feedback, points, achievements = self.reps, "Error", self.points, []

                # Update metrics
                self.reps = reps
                self.feedback = feedback
                self.reps_label.setText(f"Repetitions: {self.reps}")
                self.points_label.setText(f"Points: {self.points}")
                self.feedback_label.setText(f"Feedback: {self.feedback}")

                # Update angles display
                # Assuming that process method can provide angles; if not, adjust accordingly
                # Here, we calculate angles again for display purposes
                if self.current_exercise in ["Knee Exercise", "Squat Exercise"]:
                    hip = relevant_landmarks['hip']
                    knee = relevant_landmarks['knee']
                    ankle = relevant_landmarks['ankle']
                    knee_angle = calculate_angle(hip, knee, ankle)
                    self.knee_angle_label.setText(f"Knee Angle: {int(knee_angle)}°")
                elif self.current_exercise == "Back Exercise":
                    upper_back = relevant_landmarks['upper_back']
                    lower_back = relevant_landmarks['lower_back']
                    hips = relevant_landmarks['hips']
                    back_angle = calculate_angle(upper_back, lower_back, hips)
                    self.back_angle_label.setText(f"Back Angle: {int(back_angle)}°")

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

                # Handle Achievements
                if feedback == "Good Rep":
                    if achievements:
                        achievement_text = ", ".join(achievements)
                        self.achievement_label.setText(f"Achievements: {achievement_text}")
                        QMessageBox.information(self, "Achievement Unlocked", f"{achievements[-1]}")

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
