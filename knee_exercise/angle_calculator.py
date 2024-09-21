# angle_calculator.py
import numpy as np

def calculate_angle(a, b, c):
    """
    Calculate the angle at point b given three points a, b, c.
    Each point is a list or array with two elements: [x, y].
    """
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle