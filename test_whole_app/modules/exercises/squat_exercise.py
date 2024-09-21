# modules/exercises/squat_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class SquatExercise:
    def __init__(self,
                 knee_angle_threshold_down=120,
                 knee_angle_threshold_up=160,
                 back_angle_threshold_min=170,  # New threshold for back angle
                 back_angle_threshold_max=190,  # Allow some flexibility
                 min_hold_time=0.5):
        """
        Initialize the SquatExercise with specific parameters.

        Parameters:
        - knee_angle_threshold_down (float): Angle below which the squat is considered 'down'.
        - knee_angle_threshold_up (float): Angle above which the squat is considered 'up'.
        - back_angle_threshold_min (float): Minimum angle to consider the back as straight.
        - back_angle_threshold_max (float): Maximum angle to consider the back as straight.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.knee_counter = ExerciseCounter(knee_angle_threshold_down, knee_angle_threshold_up, min_hold_time)
        self.back_counter = ExerciseCounter(back_angle_threshold_min, back_angle_threshold_max, min_hold_time)
        self.gamification = Gamification()
        self.correct_back = False  # Flag to track back alignment

    def process(self, landmarks):
        """
        Process the landmarks to update the squat counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of upper_back, lower_back, hips, and knees.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - knee_angle (float): Current knee angle.
        - back_angle (float): Current back angle.
        """
        # Calculate back angle
        upper_back = landmarks['upper_back']
        lower_back = landmarks['lower_back']
        hips = landmarks['hips']

        back_angle = calculate_angle(upper_back, lower_back, hips)

        # Check if back is straight
        if 170 <= back_angle <= 190:
            self.correct_back = True
            back_feedback = "Back Straight"
        else:
            self.correct_back = False
            back_feedback = "Keep Your Back Straight"

        # Calculate knee angle
        hip = landmarks['hip']
        knee = landmarks['knee']
        ankle = landmarks['ankle']

        knee_angle = calculate_angle(hip, knee, ankle)

        # Update knee counter
        reps, knee_feedback = self.knee_counter.update(knee_angle)

        # Combine feedback
        if self.correct_back:
            feedback = knee_feedback
        else:
            feedback = back_feedback

        # Only add points if both knee and back are in correct position
        if reps > 0 and self.correct_back:
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback, points, achievements, knee_angle, back_angle
