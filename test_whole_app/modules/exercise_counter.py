# modules/exercise_counter.py

import time

class ExerciseCounter:
    def __init__(self, angle_threshold, min_hold_time=0.5):
        """
        Initialize the ExerciseCounter.

        Parameters:
        - angle_threshold (float): The angle threshold to consider a rep complete.
        - min_hold_time (float): Minimum time in seconds to hold a position before counting.
        """
        self.angle_threshold = angle_threshold
        self.min_hold_time = min_hold_time
        self.state = False  # False: Not in rep, True: In rep
        self.last_time = 0
        self.count = 0

    def update(self, angle):
        """
        Update the counter based on the current angle.

        Parameters:
        - angle (float): The current angle.

        Returns:
        - reps (int): Total repetitions.
        - feedback (str): Feedback message.
        """
        current_time = time.time()
        feedback = "Good Rep"

        if not self.state and angle > self.angle_threshold:
            self.state = True
            self.last_time = current_time
        elif self.state and angle < self.angle_threshold:
            if current_time - self.last_time >= self.min_hold_time:
                self.count += 1
                self.state = False
            else:
                feedback = "Hold position longer"

        return self.count, feedback
