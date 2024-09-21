# modules/exercises/back_exercise.py

from test_whole_app.modules.exercise_counter import ExerciseCounter
from test_whole_app.modules.gamification import Gamification
from test_whole_app.modules.angle_calculator import calculate_angle

class BackExercise:
    def __init__(self, angle_threshold_down=70, angle_threshold_up=110, min_hold_time=0.5):
        """
        Initialize the BackExercise with specific parameters.

        Parameters:
        - angle_threshold_down (float): Angle below which the back bend is considered 'down'.
        - angle_threshold_up (float): Angle above which the back is considered 'up'.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = ExerciseCounter(angle_threshold_down, angle_threshold_up, min_hold_time)
        self.gamification = Gamification()
        self.correct_orientation = False  # Flag to track sideways orientation

    def process(self, landmarks):
        """
        Process the landmarks to update the exercise counter and gamification.

        Parameters:
        - landmarks (dict): Contains the x and y coordinates of upper_back, lower_back, and hips.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        - points (int): Total points.
        - achievements (list): List of unlocked achievements.
        - back_angle (float): Current back angle.
        - orientation_feedback (str): Feedback regarding orientation.
        """
        upper_back = landmarks['upper_back']
        lower_back = landmarks['lower_back']
        hips = landmarks['hips']

        # Calculate back angle
        back_angle = calculate_angle(upper_back, lower_back, hips)

        # Check if back is straight
        if 170 <= back_angle <= 190:
            self.correct_back = True
            back_feedback = "Back Straight"
        else:
            self.correct_back = False
            back_feedback = "Keep Your Back Straight"

        # Validate sideways orientation
        # Assuming that in sideways position, one shoulder is higher than the other
        # For simplicity, we'll compare the y-coordinates of shoulders
        # (This can be improved with more sophisticated pose analysis)
        # Extract shoulders from landmarks
        # Note: Adjusted landmark extraction based on 'upper_back' being midpoint

        # For accurate orientation, you might need to pass more landmarks or adjust the landmark extraction
        # Here, we assume 'upper_back' is the midpoint between shoulders

        # Dummy logic for orientation (needs actual side detection)
        # For now, we assume user is always sideways for Back Exercise
        self.correct_orientation = True  # Placeholder for actual orientation check
        orientation_feedback = "Sideways to Camera"

        # Calculate back angle
        reps, feedback = self.counter.update(back_angle)

        # Combine feedback
        if self.correct_back and self.correct_orientation:
            combined_feedback = feedback
        elif not self.correct_back and self.correct_orientation:
            combined_feedback = back_feedback
        elif self.correct_back and not self.correct_orientation:
            combined_feedback = "Align Sideways to Camera"
        else:
            combined_feedback = "Maintain Straight Back and Align Sideways"

        # Only add points if both back and orientation are correct
        if reps > 0 and self.correct_back and self.correct_orientation:
            self.gamification.add_points(1)
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()
        else:
            points = self.gamification.get_points()
            achievements = self.gamification.get_achievements().copy()

        return reps, combined_feedback, points, achievements, back_angle, orientation_feedback
