# modules/exercises/back_exercise.py

from modules.exercise_counter import SquatCounter
from modules.gamification import Gamification
from modules.angle_calculator import calculate_angle

class BackExercise:
    def __init__(self, angle_threshold_down=70, angle_threshold_up=110, min_hold_time=0.5):
        """
        Initialize the BackExercise with specific parameters.

        Parameters:
        - angle_threshold_down (float): Angle below which the back bend is considered 'down'.
        - angle_threshold_up (float): Angle above which the back is considered 'up'.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = SquatCounter(angle_threshold_down, angle_threshold_up, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the back counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of upper_back, lower_back, and hips.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        """
        upper_back = landmarks['upper_back']
        lower_back = landmarks['lower_back']
        hips = landmarks['hips']

        angle = calculate_angle(upper_back, lower_back, hips)

        reps, feedback = self.counter.update(angle)

        if feedback == "Good Rep":
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback, points, achievements
