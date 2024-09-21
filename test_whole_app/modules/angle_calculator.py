# modules/angle_calculator.py

import math

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points.

    Parameters:
    - a (list or tuple): [x, y] coordinates of point a.
    - b (list or tuple): [x, y] coordinates of point b (vertex).
    - c (list or tuple): [x, y] coordinates of point c.

    Returns:
    - angle (float): The calculated angle in degrees.
    """
    try:
        a = [a[0], a[1]]
        b = [b[0], b[1]]
        c = [c[0], c[1]]

        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]

        # Calculate the dot product and magnitudes
        dot_product = ba[0]*bc[0] + ba[1]*bc[1]
        magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
        magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)

        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0

        # Calculate the angle in radians and then convert to degrees
        angle_rad = math.acos(dot_product / (magnitude_ba * magnitude_bc))
        angle_deg = math.degrees(angle_rad)

        return angle_deg
    except Exception as e:
        print(f"Error calculating angle: {e}")
        return 0
