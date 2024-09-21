# view_progress.py

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime


def fetch_progress(db_name='progress.db', exercise='Knee Exercise'):
    """
    Fetch all progress records for a specific exercise from the database.

    Parameters:
    - db_name (str): Name of the SQLite database file.
    - exercise (str): Name of the exercise to filter by.

    Returns:
    - list of tuples: Each tuple contains (date, exercise, repetitions, points).
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM progress WHERE exercise = ?", (exercise,))
    data = c.fetchall()
    conn.close()
    return data


def plot_progress(data, exercise='Knee Exercise'):
    """
    Plot repetitions and points over time.

    Parameters:
    - data (list of tuples): Each tuple contains (date, exercise, repetitions, points).
    - exercise (str): Name of the exercise for labeling.
    """
    if not data:
        print("No progress data available.")
        return

    dates = [datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S") for record in data]
    reps = [record[2] for record in data]
    points = [record[3] for record in data]

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.plot(dates, reps, marker='o', linestyle='-')
    plt.title(f'{exercise} Repetitions Over Time')
    plt.xlabel('Date')
    plt.ylabel('Repetitions')
    plt.xticks(rotation=45)

    plt.subplot(1, 2, 2)
    plt.plot(dates, points, marker='o', color='orange', linestyle='-')
    plt.title(f'{exercise} Points Over Time')
    plt.xlabel('Date')
    plt.ylabel('Points')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


def main():
    exercise = 'Knee Exercise'  # Change as needed
    data = fetch_progress(exercise=exercise)
    plot_progress(data, exercise=exercise)


if __name__ == "__main__":
    main()
