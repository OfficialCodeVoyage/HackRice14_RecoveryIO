# modules/exercise_counter.py

import time

class ExerciseCounter:
    def __init__(self, angle_threshold_down=140, angle_threshold_up=160, min_hold_time=0.5):
        """
        Initialize the ExerciseCounter with angle thresholds and minimum hold time.

        Parameters:
        - angle_threshold_down (float): Angle below which the exercise is considered 'down'.
        - angle_threshold_up (float): Angle above which the exercise is considered 'up'.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.counter = 0
        self.stage = "up"
        self.angle_threshold_down = angle_threshold_down
        self.angle_threshold_up = angle_threshold_up
        self.min_hold_time = min_hold_time  # in seconds
        self.last_transition_time = time.time()

    def update(self, angle):
        """
        Update the exercise counter based on the current angle.

        Parameters:
        - angle (float): The current angle of the knee.

        Returns:
        - counter (int): The total number of repetitions.
        - feedback (str): Feedback message based on the angle.
        """
        current_time = time.time()
        feedback = ""

        if angle > self.angle_threshold_up and self.stage == "down":
            if (current_time - self.last_transition_time) >= self.min_hold_time:
                self.stage = "up"
                self.counter += 1
                feedback = "Good Rep"
                self.last_transition_time = current_time
        elif angle < self.angle_threshold_down and self.stage == "up":
            if (current_time - self.last_transition_time) >= self.min_hold_time:
                self.stage = "down"
                feedback = "Go Up"
                self.last_transition_time = current_time

        return self.counter, feedback
