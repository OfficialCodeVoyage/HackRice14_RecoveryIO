# modules/database.py

import sqlite3
from datetime import datetime

class ProgressTracker:
    def __init__(self, db_name='progress.db'):
        """
        Initialize the ProgressTracker with a SQLite database.

        Parameters:
        - db_name (str): Name of the SQLite database file.
        """
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create the necessary tables in the database if they don't exist.
        """
        # Progress table
        self.c.execute('''CREATE TABLE IF NOT EXISTS progress
                     (date TEXT, exercise TEXT, repetitions INTEGER, points INTEGER)''')
        # Achievements table
        self.c.execute('''CREATE TABLE IF NOT EXISTS achievements
                     (milestone INTEGER PRIMARY KEY, achievement TEXT)''')
        self.conn.commit()

    def record_progress(self, exercise, reps, points):
        """
        Record the progress of an exercise session.

        Parameters:
        - exercise (str): Name of the exercise performed.
        - reps (int): Number of repetitions completed.
        - points (int): Points earned during the session.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("INSERT INTO progress (date, exercise, repetitions, points) VALUES (?, ?, ?, ?)",
                      (date, exercise, reps, points))
        self.conn.commit()

    def fetch_progress(self, exercise=None):
        """
        Fetch all progress records, optionally filtered by exercise.

        Parameters:
        - exercise (str, optional): Name of the exercise to filter by.

        Returns:
        - list of tuples: Each tuple contains (date, exercise, repetitions, points).
        """
        if exercise:
            self.c.execute("SELECT * FROM progress WHERE exercise = ?", (exercise,))
        else:
            self.c.execute("SELECT * FROM progress")
        return self.c.fetchall()

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
