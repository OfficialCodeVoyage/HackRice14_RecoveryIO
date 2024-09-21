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
        - knee_angle_threshold (float): Angle below which the squat is considered down.
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
        - landmarks (dict): Contains the x and y coordinates of hip, knee, ankle, shoulder_left, shoulder_right.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - knee_angle (float): Current knee angle.
        - back_angle (float): Current back angle.
        """
        try:
            hip = landmarks['hip']
            knee = landmarks['knee']
            ankle = landmarks['ankle']
            shoulder_left = landmarks.get('shoulder_left', hip)  # Use hip if shoulder landmarks are missing
            shoulder_right = landmarks.get('shoulder_right', hip)

            knee_angle = calculate_angle(hip, knee, ankle)

            # Calculate back angle using shoulders and hips
            avg_shoulder = [(shoulder_left[0] + shoulder_right[0]) / 2, (shoulder_left[1] + shoulder_right[1]) / 2]
            back_angle = calculate_angle(shoulder_left, hip, shoulder_right)

            reps_knee, feedback_knee = self.knee_counter.update(knee_angle)
            reps_back, feedback_back = self.back_counter.update(back_angle)

            reps = min(reps_knee, reps_back)
            feedback = "Good Rep" if feedback_knee == "Good Rep" and feedback_back == "Good Rep" else "Form Correction Needed"

            if feedback == "Good Rep":
                self.gamification.add_points(2)
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()
            else:
                points = self.gamification.get_points()
                achievements = self.gamification.get_achievements().copy()

            return reps, feedback, points, achievements, knee_angle, back_angle
        except KeyError as e:
            print(f"Error processing exercise: {e}")
            return self.knee_counter.count, "Error", self.gamification.get_points(), [], None, None
