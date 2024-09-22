# gamification.py

class Gamification:
    def __init__(self):
        """
        Initialize the Gamification system with points and achievements.
        """
        self.points = 0
        self.achievements = []
        self.milestones = {
            10: "10 Reps",
            50: "50 Reps",
            100: "100 Reps",
            200: "200 Reps"
        }

    def add_points(self, reps):
        """
        Add points based on the number of repetitions.

        Parameters:
        - reps (int): Number of repetitions to add points for.
        """
        self.points += reps * 10  # 10 points per rep
        self.check_achievements()

    def check_achievements(self):
        """
        Check and update achievements based on current points.
        """
        for milestone, achievement in self.milestones.items():
            if self.points >= milestone and achievement not in self.achievements:
                self.achievements.append(achievement)
                print(f"Achievement Unlocked: {achievement}")

    def get_points(self):
        """
        Retrieve the current points.

        Returns:
        - points (int): Total points earned.
        """
        return self.points

    def get_achievements(self):
        """
        Retrieve the list of unlocked achievements.

        Returns:
        - achievements (list): List of achievement strings.
        """
        return self.achievements
