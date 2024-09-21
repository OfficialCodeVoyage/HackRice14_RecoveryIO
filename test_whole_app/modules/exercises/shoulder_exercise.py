# modules/exercises/shoulder_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class ShoulderExercise:
    def __init__(self, angle_threshold_down=60, angle_threshold_up=120, min_hold_time=0.5):
        """
        Initialize the ShoulderExercise with specific parameters.

        Parameters:
        - angle_threshold_down (float): Angle below which the shoulder lift is considered 'down'.
        - angle_threshold_up (float): Angle above which the shoulder is considered 'up'.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = ExerciseCounter(angle_threshold_down, angle_threshold_up, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of shoulder, elbow, and wrist.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        """
        shoulder = landmarks['shoulder']
        elbow = landmarks['elbow']
        wrist = landmarks['wrist']

        angle = calculate_angle(shoulder, elbow, wrist)

        reps, feedback = self.counter.update(angle)

        if feedback == "Good Rep":
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback, points, achievements
