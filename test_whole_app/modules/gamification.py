# modules/gamification.py

class Gamification:
    def __init__(self):
        """
        Initialize the Gamification system.
        """
        self.points = 0
        self.achievements = []

    def add_points(self, points):
        """
        Add points to the user's total.

        Parameters:
        - points (int): The number of points to add.
        """
        self.points += points
        self.check_achievements()

    def get_points(self):
        """
        Get the total points.

        Returns:
        - int: Total points.
        """
        return self.points

    def get_achievements(self):
        """
        Get the list of achievements.

        Returns:
        - list: List of achievements.
        """
        return self.achievements

    def check_achievements(self):
        """
        Check and unlock achievements based on points.
        """
        if self.points >= 50 and "50 Points" not in self.achievements:
            self.achievements.append("50 Points")
        if self.points >= 100 and "100 Points" not in self.achievements:
            self.achievements.append("100 Points")
        # Add more achievements as needed
