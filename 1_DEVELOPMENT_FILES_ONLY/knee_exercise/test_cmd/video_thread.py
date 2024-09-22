# video_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np

from pose_estimation import PoseEstimator
from angle_calculator import calculate_angle
from exercise_counter import SquatCounter
from gamification import Gamification


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    update_reps_signal = pyqtSignal(int)
    update_feedback_signal = pyqtSignal(str)
    update_points_signal = pyqtSignal(int)
    update_achievements_signal = pyqtSignal(list)

    def __init__(self, focus_side='right'):
        super().__init__()
        self._run_flag = True
        self.pose_estimator = PoseEstimator(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.squat_counter = SquatCounter()
        self.gamification = Gamification()
        self.focus_side = focus_side.lower()
        if self.focus_side not in ['left', 'right']:
            self.focus_side = 'right'  # Default to right

    def run(self):
        # Capture from webcam
        cap = cv2.VideoCapture(0)  # Use 0 for default camera; replace with video file path if needed
        frame_width = 640
        frame_height = 480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                try:
                    # Resize frame for performance
                    frame = cv2.resize(frame, (frame_width, frame_height))

                    # Process frame with MediaPipe
                    image, results = self.pose_estimator.process_frame(frame)
                    image = self.pose_estimator.draw_landmarks(image, results)
                    landmarks = self.pose_estimator.get_landmarks(results)

                    feedback = "Ready"
                    reps = self.squat_counter.counter
                    points = self.gamification.points
                    achievements = self.gamification.achievements.copy()

                    if landmarks:
                        # Extract required landmarks based on focus_side
                        if self.focus_side == 'left':
                            hip = landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_HIP.value]
                            knee = landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_KNEE.value]
                            ankle = landmarks[self.pose_estimator.mp_pose.PoseLandmark.LEFT_ANKLE.value]
                        else:
                            hip = landmarks[self.pose_estimator.mp_pose.PoseLandmark.RIGHT_HIP.value]
                            knee = landmarks[self.pose_estimator.mp_pose.PoseLandmark.RIGHT_KNEE.value]
                            ankle = landmarks[self.pose_estimator.mp_pose.PoseLandmark.RIGHT_ANKLE.value]

                        # Calculate angle
                        hip_coords = [hip.x, hip.y]
                        knee_coords = [knee.x, knee.y]
                        ankle_coords = [ankle.x, ankle.y]
                        angle = calculate_angle(hip_coords, knee_coords, ankle_coords)

                        # Update squat counter
                        reps, feedback = self.squat_counter.update(angle)

                        # Update gamification
                        if feedback == "Good Rep":
                            self.gamification.add_points(1)
                            points = self.gamification.points
                            achievements = self.gamification.achievements.copy()

                        # Emit signals
                        self.update_reps_signal.emit(reps)
                        self.update_feedback_signal.emit(feedback)
                        self.update_points_signal.emit(points)
                        self.update_achievements_signal.emit(achievements)

                        # Annotate angle on frame
                        h, w, _ = frame.shape
                        knee_coords_pixel = (int(knee.x * w), int(knee.y * h))
                        color = (0, 255, 0)  # Default color
                        if feedback == "Too Low!":
                            color = (0, 0, 255)  # Red
                        elif feedback == "Good Rep":
                            color = (0, 255, 0)  # Green
                        else:
                            color = (255, 255, 0)  # Yellow

                        cv2.putText(image, f"{int(angle)}°", knee_coords_pixel, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2,
                                    cv2.LINE_AA)

                    # Emit the processed image
                    self.change_pixmap_signal.emit(image)

                except Exception as e:
                    print(f"Error in VideoThread: {e}")

        # Release the video capture when the thread is stopped
        cap.release()
        self.pose_estimator.close()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()
