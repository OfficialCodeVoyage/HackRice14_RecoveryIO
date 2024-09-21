# modules/database.py

import sqlite3
import os
from datetime import datetime

class ProgressTracker:
    def __init__(self, db_path='progress.db'):
        """
        Initialize the ProgressTracker with a SQLite database.

        Parameters:
        - db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        """
        Create the progress table if it doesn't exist.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise TEXT NOT NULL,
                    repetitions INTEGER NOT NULL,
                    points INTEGER NOT NULL,
                    date TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def record_progress(self, exercise, repetitions, points):
        """
        Record the progress of an exercise.

        Parameters:
        - exercise (str): Name of the exercise.
        - repetitions (int): Number of repetitions completed.
        - points (int): Points earned.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO progress (exercise, repetitions, points, date)
                VALUES (?, ?, ?, ?)
            ''', (exercise, repetitions, points, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error recording progress: {e}")

    def get_all_progress(self):
        """
        Retrieve all progress records.

        Returns:
        - list of tuples: Each tuple represents a progress record.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM progress')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching progress: {e}")
            return []

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
