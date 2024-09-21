# database.py

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
        self.create_table()

    def create_table(self):
        """
        Create the 'progress' table in the database if it doesn't exist.
        """
        self.c.execute('''CREATE TABLE IF NOT EXISTS progress
                     (date TEXT, repetitions INTEGER, points INTEGER)''')
        self.conn.commit()

    def record_progress(self, reps, points):
        """
        Record the progress of an exercise session.

        Parameters:
        - reps (int): Number of repetitions completed.
        - points (int): Points earned during the session.
        """
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("INSERT INTO progress (date, repetitions, points) VALUES (?, ?, ?)",
                      (date, reps, points))
        self.conn.commit()

    def fetch_progress(self):
        """
        Fetch all progress records.

        Returns:
        - list of tuples: Each tuple contains (date, repetitions, points).
        """
        self.c.execute("SELECT * FROM progress")
        return self.c.fetchall()

    def close(self):

        """
        Close the database connection.
        """
        self.conn.close()
