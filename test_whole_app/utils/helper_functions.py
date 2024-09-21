# utils/helper_functions.py

from PyQt5.QtGui import QImage, QPixmap
import cv2

def convert_cv_qt(cv_img):
    """
    Convert from an OpenCV image to QPixmap for display in PyQt5.

    Parameters:
    - cv_img (numpy.ndarray): OpenCV image.

    Returns:
    - QPixmap: Image converted to Qt format.
    """
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qt_image)
