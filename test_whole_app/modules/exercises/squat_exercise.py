# modules/exercises/squat_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class SquatExercise:
    def __init__(self,
                 knee_angle_threshold=160,
                 back_angle_threshold=160,
                 min_hold_time=0.5):
        """
        Initialize the SquatExercise with specific parameters.

        Parameters:
        - knee_angle_threshold (float): Angle above which the squat is considered up.
        - back_angle_threshold (float): Angle above which the back is considered straight.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.knee_counter = ExerciseCounter(knee_angle_threshold, min_hold_time)
        self.back_counter = ExerciseCounter(back_angle_threshold, min_hold_time)
        self.gamification = Gamification()

    def process(self, landmarks):
        """
        Process the landmarks to update the squat exercise counters and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of hip, knee, ankle, upper_back, and lower_back.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - knee_angle (float): Current knee angle.
        - back_angle (float): Current back angle.
        """
        hip = landmarks['hip']
        knee = landmarks['knee']
        ankle = landmarks['ankle']
        upper_back = landmarks['upper_back']
        lower_back = landmarks['lower_back']

        knee_angle = calculate_angle(hip, knee, ankle)
        back_angle = calculate_angle(upper_back, lower_back, hip)

        knee_reps, knee_feedback = self.knee_counter.update(knee_angle)
        back_reps, back_feedback = self.back_counter.update(back_angle)

        reps = min(knee_reps, back_reps)
        feedback = "Good Rep" if knee_feedback == "Good Rep" and back_feedback == "Good Rep" else "Form Correction Needed"

        if feedback == "Good Rep":
            self.gamification.add_points(2)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, feedback, points, achievements, knee_angle, back_angle
