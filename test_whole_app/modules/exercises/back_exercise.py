# modules/exercises/back_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class BackExercise:
    def __init__(self, angle_threshold_min=170, angle_threshold_max=190, min_hold_time=0.5):
        """
        Initialize the BackExercise with specific parameters.

        Parameters:
        - angle_threshold_min (float): Minimum angle to consider the back as straight.
        - angle_threshold_max (float): Maximum angle to consider the back as straight.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.back_counter = ExerciseCounter(angle_threshold_min, angle_threshold_max, min_hold_time)
        self.gamification = Gamification()
        self.correct_position = False  # Flag to track if user is sideways

    def process(self, landmarks):
        """
        Process the landmarks to update the back exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of upper_back, lower_back, and hips.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - back_angle (float): Current back angle.
        """
        upper_back = landmarks['upper_back']
        lower_back = landmarks['lower_back']
        hips = landmarks['hips']

        back_angle = calculate_angle(upper_back, lower_back, hips)

        # Check if back is straight
        if 170 <= back_angle <= 190:
            self.correct_position = True
            back_feedback = "Back Straight"
        else:
            self.correct_position = False
            back_feedback = "Keep Your Back Straight"

        # Update back counter
        reps, feedback = self.back_counter.update(back_angle)

        # Combine feedback
        if self.correct_position:
            feedback_message = feedback
        else:
            feedback_message = back_feedback

        # Only add points if back is in correct position
        if reps > 0 and self.correct_position:
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback_message, points, achievements, back_angle
