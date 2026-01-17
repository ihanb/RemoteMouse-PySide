"""摄像头处理模块，负责摄像头的打开、关闭和帧捕获"""

import cv2
import platform
from constants import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS


class CameraHandler:
    """摄像头处理器类，负责摄像头的基本操作"""
    
    def __init__(self):
        self.cap = None
        self.current_camera_info = {}
    
    def open_camera(self, camera_index):
        """打开指定索引的摄像头"""
        # 释放之前的摄像头（如果已打开）
        if self.cap is not None:
            self.cap.release()
            
        # 打开新摄像头
        self.cap = cv2.VideoCapture(camera_index)
        if self.cap.isOpened():
            # 设置摄像头参数以获得更好的性能
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            return True
        return False
    
    def close_camera(self):
        """关闭当前摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def read_frame(self):
        """读取当前摄像头帧"""
        if self.cap is not None and self.cap.isOpened():
            return self.cap.read()
        return False, None
    
    def is_opened(self):
        """检查摄像头是否已打开"""
        return self.cap is not None and self.cap.isOpened()
    
    def get_camera_name_by_index(self, device_id, camera_list):
        """根据摄像头索引获取名称"""
        # 如果是笔记本内置摄像头
        if device_id == 0 and len(camera_list) == 1:
            return "内置摄像头"
        elif device_id == 0:
            return "主摄像头"
        elif device_id == 1:
            return "副摄像头"
        else:
            return f"摄像头 {device_id}"

    def get_camera_name_windows(self, device_id):
        """在Windows系统上获取摄像头设备名称"""
        try:
            # 检测摄像头是否可用
            cap = cv2.VideoCapture(device_id)
            if cap.isOpened():
                cap.release()
                # 简单返回基础名称
                return f"摄像头 {device_id}"
            else:
                return f"不可用的摄像头 {device_id}"
        except Exception as e:
            print(f"检测摄像头 {device_id} 时出错: {e}")
            return f"摄像头 {device_id}"

    def get_camera_name(self, device_id):
        """获取摄像头设备名称"""
        system = platform.system()
        if system == "Windows":
            return self.get_camera_name_windows(device_id)
        else:
            # 对于非Windows系统，返回默认名称
            return f"摄像头 {device_id}"

    def search_cameras(self):
        """搜索本地摄像头设备"""
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # 测试摄像头是否真正可用（尝试读取一帧）
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
            else:
                break
        
        # 根据摄像头数量为其分配更有意义的名称
        cameras_info = {}
        for idx, cam_id in enumerate(available_cameras):
            if len(available_cameras) == 1:
                camera_name = f"内置摄像头 ({cam_id})"
            elif idx == 0:
                camera_name = f"主摄像头 ({cam_id})"
            elif idx == 1:
                camera_name = f"副摄像头 ({cam_id})"
            else:
                camera_name = f"外接摄像头 {idx+1} ({cam_id})"
                
            cameras_info[cam_id] = {
                'id': cam_id,
                'name': camera_name.split(' (')[0]  # 提取名称部分
            }
        
        return available_cameras, cameras_info