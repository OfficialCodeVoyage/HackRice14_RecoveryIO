# gui.py
import cProfile
import pstats
import sys

import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from video_thread import VideoThread
from database import ProgressTracker
import matplotlib.pyplot as plt

import pyttsx3

class RehabApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Knee Rehabilitation App')
        self.setGeometry(100, 100, 1000, 700)

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
        self.timer_label = QLabel('Time: 00:00')
        self.feedback_label = QLabel('Feedback: Ready')
        self.points_label = QLabel('Points: 0')
        self.achievements_label = QLabel('Achievements: None')

        self.progress_button = QPushButton('Show Progress')

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.counter_label)
        stats_layout.addWidget(self.timer_label)
        stats_layout.addWidget(self.points_label)
        stats_layout.addWidget(self.achievements_label)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(stats_layout)
        main_layout.addWidget(self.feedback_label)
        main_layout.addWidget(self.progress_button)

        self.setLayout(main_layout)

        # Initialize Video Thread
        # Focus on the right knee
        self.focus_side = 'right'  # Change to 'left' if needed
        self.thread = VideoThread(focus_side=self.focus_side)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_reps_signal.connect(self.update_reps)
        self.thread.update_feedback_signal.connect(self.update_feedback)
        self.thread.update_points_signal.connect(self.update_points)
        self.thread.update_achievements_signal.connect(self.update_achievements)

        # Connect Buttons
        self.start_button.clicked.connect(self.start_exercise)
        self.stop_button.clicked.connect(self.stop_exercise)
        self.progress_button.clicked.connect(self.show_progress)

        # Timer for exercise duration
        self.exercise_timer = 0
        self.timer_running = False

    def start_exercise(self):
        self.thread = VideoThread(focus_side=self.focus_side)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_reps_signal.connect(self.update_reps)
        self.thread.update_feedback_signal.connect(self.update_feedback)
        self.thread.update_points_signal.connect(self.update_points)
        self.thread.update_achievements_signal.connect(self.update_achievements)
        self.thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer_running = True
        self.exercise_timer = 0
        self.update_timer_label()

    def stop_exercise(self):
        self.thread.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer_running = False

        # Record progress
        reps = int(self.counter_label.text().split(": ")[1])
        points = int(self.points_label.text().split(": ")[1])
        self.progress_tracker.record_progress(reps, points)

        QMessageBox.information(self, "Session Stopped", "Your exercise session has been stopped and progress has been saved.")

    def update_timer_label(self):
        if self.timer_running:
            self.exercise_timer += 1
            mins, secs = divmod(self.exercise_timer, 60)
            time_str = f"Time: {mins:02d}:{secs:02d}"
            self.timer_label.setText(time_str)
            QTimer.singleShot(1000, self.update_timer_label)

    def speak_feedback(self, feedback):
        if feedback != self.last_feedback:
            self.engine.say(feedback)
            self.engine.runAndWait()
            self.last_feedback = feedback

    def update_image(self, cv_img):
        """Updates the video_label with a new OpenCV image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.video_label.setPixmap(qt_img)

    def update_reps(self, reps):
        self.counter_label.setText(f"Repetitions: {reps}")

    def update_feedback(self, feedback):
        self.feedback_label.setText(f"Feedback: {feedback}")
        self.speak_feedback(feedback)

    def update_points(self, points):
        self.points_label.setText(f"Points: {points}")

    def update_achievements(self, achievements):
        if achievements:
            self.achievements_label.setText(f"Achievements: {', '.join(achievements)}")
        else:
            self.achievements_label.setText("Achievements: None")

    def convert_cv_qt(self, cv_img):
        """Convert from an OpenCV image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def show_progress(self):
        progress = self.progress_tracker.fetch_progress()
        if progress:
            dates = [record[0] for record in progress]
            reps = [record[1] for record in progress]
            points = [record[2] for record in progress]

            plt.figure(figsize=(10,5))
            plt.subplot(1, 2, 1)
            plt.plot(dates, reps, marker='o')
            plt.title('Repetitions Over Time')
            plt.xlabel('Date')
            plt.ylabel('Repetitions')
            plt.xticks(rotation=45)

            plt.subplot(1, 2, 2)
            plt.plot(dates, points, marker='o', color='orange')
            plt.title('Points Over Time')
            plt.xlabel('Date')
            plt.ylabel('Points')
            plt.xticks(rotation=45)

            plt.tight_layout()
            plt.show()
        else:
            QMessageBox.information(self, "No Data", "No progress data available to display.")

    def closeEvent(self, event):
        self.thread.stop()
        self.progress_tracker.close()
        self.engine.stop()
        event.accept()

def main():
    # Your main application code
    app = QApplication(sys.argv)
    window = RehabApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)  # Adjust the number to display more/less functions