"""工具函数模块"""

import cv2
import numpy as np
from PySide6.QtGui import QImage


def calculate_distance(point1, point2):
    """计算两点之间的欧几里得距离"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def normalize_coordinates(x, y, width, height):
    """将像素坐标标准化为0-1范围内的坐标"""
    norm_x = max(0.0, min(1.0, x / width))
    norm_y = max(0.0, min(1.0, y / height))
    return norm_x, norm_y


def denormalize_coordinates(norm_x, norm_y, width, height):
    """将标准化坐标转换回像素坐标"""
    x = int(norm_x * width)
    y = int(norm_y * height)
    return x, y


def get_screen_size():
    """获取屏幕尺寸"""
    try:
        import pyautogui
        return pyautogui.size()
    except ImportError:
        # 默认屏幕尺寸
        return 1920, 1080


def convert_cv_to_qt_image(cv_image):
    """将OpenCV图像转换为Qt图像"""
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return qt_image


def check_module_availability(module_name):
    """检查模块是否可用"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False