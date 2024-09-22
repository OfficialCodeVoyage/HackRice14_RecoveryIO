# modules/exercises/back_exercise.py

from modules.exercise_counter import ExerciseCounter
from modules.gamification import Gamification
from modules.angle_calculator import calculate_angle

class BackExercise:
    def __init__(self,
                 back_angle_threshold=160,
                 min_hold_time=0.5):
        """
        Initialize the BackExercise with specific parameters.

        Parameters:
        - back_angle_threshold (float): Angle above which the back is considered straight.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = ExerciseCounter(back_angle_threshold, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the back exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of left_shoulder, right_shoulder, left_hip, right_hip.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - back_angle (float): Current back angle.
        """
        try:
            left_shoulder = landmarks['left_shoulder']
            right_shoulder = landmarks['right_shoulder']
            left_hip = landmarks['left_hip']
            right_hip = landmarks['right_hip']

            # Calculate back angle using shoulders and hips
            hip = [(left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2]
            shoulder = [(left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2]
            back_angle = calculate_angle(left_shoulder, hip, shoulder)

            reps, feedback = self.counter.update(back_angle)

            if feedback == "Good Rep":
                self.gamification.add_points(1)
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()
            else:
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()

            return reps, feedback, points, achievements, back_angle
        except KeyError as e:
            print(f"Error processing exercise: {e}")
            return self.counter.count, "Error", self.gamification.get_points(), [], None
