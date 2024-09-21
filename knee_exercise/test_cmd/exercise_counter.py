# exercise_counter.py

class SquatCounter:
    def __init__(self, angle_threshold_down=140, angle_threshold_up=160):
        self.counter = 0
        self.stage = "up"
        self.angle_threshold_down = angle_threshold_down
        self.angle_threshold_up = angle_threshold_up

    def update(self, angle):
        """
        Update the squat counter based on the current knee angle.

        Parameters:
        - angle (float): The current angle of the knee.

        Returns:
        - counter (int): The total number of repetitions.
        - feedback (str): Feedback message based on the angle.
        """
        feedback = ""
        if angle > self.angle_threshold_up and self.stage == "down":
            self.stage = "up"
            self.counter += 1
            feedback = "Good Rep"
        elif angle < self.angle_threshold_down and self.stage == "up":
            self.stage = "down"
            feedback = "Go Up"

        return self.counter, feedback
