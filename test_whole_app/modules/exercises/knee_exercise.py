# modules/exercises/knee_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class KneeExercise:
    def __init__(self,
                 angle_threshold_down=160,
                 min_hold_time=0.5):
        """
        Initialize the KneeExercise with specific parameters.

        Parameters:
        - angle_threshold_down (float): Angle below which the squat is considered down.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = ExerciseCounter(angle_threshold_down, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the knee exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of hip, knee, ankle.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - knee_angle (float): Current knee angle.
        """
        try:
            hip = landmarks['hip']
            knee = landmarks['knee']
            ankle = landmarks['ankle']

            knee_angle = calculate_angle(hip, knee, ankle)

            reps, feedback = self.counter.update(knee_angle)

            if feedback == "Good Rep":
                self.gamification.add_points(1)
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()
            else:
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()

            return reps, feedback, points, achievements, knee_angle
        except KeyError as e:
            print(f"Error processing exercise: {e}")
            return self.counter.count, "Error", self.gamification.get_points(), [], None
