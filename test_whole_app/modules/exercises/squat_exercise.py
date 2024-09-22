# modules/exercises/squat_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class SquatExercise:
    def __init__(self,
                 knee_angle_threshold=100,  # Lowered threshold
                 min_hold_time=0.5):
        """
        Initialize the SquatExercise with specific parameters.

        Parameters:
        - knee_angle_threshold (float): Angle below which the squat is considered down.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.knee_counter = ExerciseCounter(knee_angle_threshold, min_hold_time, reverse=True)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the squat exercise counters and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of hip, knee, ankle.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - knee_angle (float): Current knee angle.
        - back_angle (None): Removed from rep counting.
        """
        try:
            hip = landmarks['hip']
            knee = landmarks['knee']
            ankle = landmarks['ankle']

            knee_angle = calculate_angle(hip, knee, ankle)

            reps_knee, feedback_knee = self.knee_counter.update(knee_angle)

            reps = reps_knee
            feedback = feedback_knee

            if feedback == "Good Rep":
                self.gamification.add_points(2)
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()
            else:
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()

            return reps, feedback, points, achievements, knee_angle, None  # back_angle removed
        except KeyError as e:
            print(f"Error processing exercise: {e}")
            return self.knee_counter.count, "Error", self.gamification.get_points(), [], None, None
