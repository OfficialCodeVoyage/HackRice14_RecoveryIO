# gui/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout,
                             QWidget, QComboBox, QSpinBox, QMessageBox, QHBoxLayout, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QFont, QMovie, QIcon

import cv2
import sys
import os

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
        self.setGeometry(100, 100, 1400, 800)  # Increased window size for better layout

        # Apply Style Sheet
        self.apply_stylesheet()

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

    def apply_stylesheet(self):
        """
        Apply the QSS stylesheet to the application.
        """
        style_path = os.path.join('assets', 'styles', 'style.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print("Style sheet not found. Proceeding without it.")

    def setup_ui(self):
        """
        Setup the main UI components.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()  # Split into left and right columns

        # Left Column Layout for Video and Tutorial
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(30, 30, 0, 0)

        # Video Display
        self.video_label = QLabel()
        self.video_label.setFixedSize(800, 600)  # Adjusted size to fit layout
        self.video_label.setStyleSheet("border: 2px solid #555;")
        self.video_label.setAlignment(Qt.AlignCenter)

        # Tutorial Button with Icon
        self.tutorial_button = QPushButton("  View Tutorial")
        self.tutorial_button.setIcon(QIcon(os.path.join('assets', 'icons', 'tutorial.png')))
        self.tutorial_button.setIconSize(QSize(36, 36))
        self.tutorial_button.setFixedSize(200, 40)
        self.tutorial_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;  /* Increase font size for better readability */
                padding: 10px;    /* Add padding for better spacing */
            }
        """)
        self.tutorial_button.clicked.connect(self.view_tutorial)

        # Add video and tutorial button to left layout
        left_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.tutorial_button, alignment=Qt.AlignCenter)
        left_layout.addStretch()

        # Right Column Layout for Controls and Instructions
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 30, 30, 0)
        # Top Controls Layout
        controls_layout = QHBoxLayout()

        # Exercise Selection
        self.exercise_label = QLabel("Exercise:")
        self.exercise_label.setFont(QFont("Arial", 18))
        self.exercise_combo = QComboBox()
        self.exercise_combo.addItems(self.exercises.keys())
        self.exercise_combo.setFixedWidth(150)
        self.exercise_combo.currentTextChanged.connect(self.change_exercise)

        # Goal Setting
        self.goal_label = QLabel("Set Goal (Reps):")
        self.goal_label.setFont(QFont("Arial", 18))
        self.goal_spinbox = QSpinBox()
        self.goal_spinbox.setRange(1, 1000)
        self.goal_spinbox.setValue(20)  # Default goal
        self.goal_spinbox.setFixedWidth(100)

        # Start/Stop Button with Icon
        self.start_button = QPushButton("Start Exercise")
        self.start_button.setIcon(QIcon(os.path.join('assets', 'icons', 'start.png')))
        self.start_button.setIconSize(QSize(36, 36))
        self.start_button.setFixedSize(200, 100)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;  /* Increase font size for better readability */
                padding: 10px;    /* Add padding for better spacing */
            }
        """)
        self.start_button.clicked.connect(self.toggle_exercise)



        # Add widgets to controls layout
        controls_layout.addWidget(self.exercise_label)
        controls_layout.addWidget(self.exercise_combo)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.goal_label)
        controls_layout.addWidget(self.goal_spinbox)
        controls_layout.addSpacing(20)
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
        self.knee_angle_label.setStyleSheet("color: #333333;")

        self.back_angle_label = QLabel("Back Angle: --°")
        self.back_angle_label.setFont(QFont("Arial", 14))
        self.back_angle_label.setStyleSheet("color: #333333;")

        self.shoulder_angle_label = QLabel("Shoulder Angle: --°")
        self.shoulder_angle_label.setFont(QFont("Arial", 14))
        self.shoulder_angle_label.setStyleSheet("color: #333333;")

        angles_layout.addWidget(self.knee_angle_label)
        angles_layout.addWidget(self.back_angle_label)
        angles_layout.addWidget(self.shoulder_angle_label)

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
        self.progress_bar.setFixedHeight(25)

        # Achievement Label (Removed Pop-ups)
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
        self.instructions_text.setFixedHeight(300)
        self.instructions_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 18px;
            }
        """)
        self.set_instructions("Knee Exercise", """
        <b>1. Stand upright with feet shoulder-width apart.</b>
        <b><br>2. Bend your knees to lower your body as if sitting back into a chair.</b>
        <b><br>3. Keep your back straight and chest up.</b>
        <b><br>4. Lower until your thighs are parallel to the ground.</b>
        <b><br>5. Push through your heels to return to the starting position.</b>
        """)

        # Add widgets to right layout
        right_layout.addLayout(controls_layout)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.feedback_label)
        right_layout.addSpacing(10)
        right_layout.addLayout(angles_layout)
        right_layout.addSpacing(10)
        right_layout.addLayout(reps_points_layout)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.progress_bar)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.achievement_label)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.instructions_label)
        right_layout.addWidget(self.instructions_text)
        right_layout.addStretch()

        # Add left and right layouts to main layout with margins
        main_layout.addLayout(left_layout, stretch=2)  # Video and Tutorial
        main_layout.addSpacing(30)  # Add margin between columns
        main_layout.addLayout(right_layout, stretch=1)  # Controls and Instructions

        central_widget.setLayout(main_layout)

        # Initialize Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def set_instructions(self, exercise, instructions):
        """
        Set instructions based on the selected exercise.

        Parameters:
        - exercise (str): Current exercise name.
        - instructions (str): Instruction text.
        """
        self.instructions_text.setText(instructions.lstrip())

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
        instructions_dict = {
            "Knee Exercise": """
    - Stand upright with feet shoulder-width apart.
    - Bend your knees to lower your body as if sitting back into a chair.
    - Keep your back straight and chest up.
    - Lower until your thighs are parallel to the ground.
    - Push through your heels to return to the starting position.
                    """,
            "Shoulder Exercise": """
    - Stand or sit upright with your back straight.
    - Extend your arms out to the sides at shoulder height.
    - Slowly raise your arms above your head, keeping them straight.
    - Hold for a moment at the top.
    - Lower your arms back to the starting position.
    - Repeat for the desired number of repetitions.
                    """,
            "Back Exercise": """
    - Stand sideways to the camera for optimal back alignment.
    - Place your hands on your hips.
    - Slowly bend forward at the hips, keeping your back straight.
    - Lower your torso until it's nearly parallel to the ground.
    - Hold for a few seconds.
    - Return to the starting position by contracting your back muscles.
    - Repeat for the desired number of repetitions.
                    """,
            "Squat Exercise": """
    - Stand sideways to the camera with feet shoulder-width apart.
    - Bend your knees to lower your body as if sitting back into a chair.
    - Keep your back straight and chest up. Focus on the dots on your back to maintain alignment.
    - Lower until your thighs are parallel to the ground.
    - Push through your heels to return to the starting position.
    - Repeat for the desired number of repetitions.
                    """,
        }
        instructions = instructions_dict.get(exercise_name, "No instructions available.")

        # Process instructions to add numbering and bold formatting
        lines = instructions.strip().split('\n')
        formatted_lines = []
        step_number = 1
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                # Replace '-' with step number and add bold formatting
                instruction_text = line[2:]  # Remove the '- ' from the beginning
                formatted_line = f'<b>{step_number}. {instruction_text}</b>'
                step_number += 1
            else:
                formatted_line = line
            formatted_lines.append(formatted_line)
        formatted_instructions = '<br>'.join(formatted_lines)
        return formatted_instructions

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
