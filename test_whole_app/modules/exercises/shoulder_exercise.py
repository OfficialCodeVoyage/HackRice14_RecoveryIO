# modules/exercises/shoulder_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class ShoulderExercise:
    def __init__(self,
                 angle_threshold_up=160,
                 angle_threshold_down=100,
                 min_hold_time=0.5):
        """
        Initialize the ShoulderExercise with specific parameters.

        Parameters:
        - angle_threshold_up (float): Angle above which the arm is considered raised.
        - angle_threshold_down (float): Angle below which the arm is considered lowered.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = ExerciseCounter(angle_threshold_down, angle_threshold_up, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the shoulder exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of shoulder, elbow, and wrist.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - shoulder_angle (float): Current shoulder angle.
        """
        shoulder = landmarks['shoulder']
        elbow = landmarks['elbow']
        wrist = landmarks['wrist']

        shoulder_angle = calculate_angle(shoulder, elbow, wrist)

        reps, feedback = self.counter.update(shoulder_angle)

        if feedback == "Good Rep":
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback, points, achievements, shoulder_angle
