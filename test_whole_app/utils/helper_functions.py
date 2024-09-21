# utils/helper_functions.py

import cv2
from PyQt5.QtGui import QImage, QPixmap

def convert_cv_qt(cv_img):
    """
    Convert from an OpenCV image to QPixmap.

    Parameters:
    - cv_img (numpy.ndarray): The OpenCV image.

    Returns:
    - QPixmap: The converted QPixmap.
    """
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_image)
