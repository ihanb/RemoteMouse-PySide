"""GUI主窗口模块，负责界面元素和交互逻辑"""

import sys
import cv2
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame, QCheckBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

# 导入自定义模块
from camera_handler import CameraHandler
from gesture_recognizer import GestureRecognizer
from mouse_controller import MouseController

# 检查pyautogui是否可用
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # 启用安全模式，将鼠标移到屏幕角落会暂停
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("pyautogui未安装，鼠标控制功能将不可用")


class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        from constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 检查pyautogui是否可用
        self.PYAUTOGUI_AVAILABLE = PYAUTOGUI_AVAILABLE
        
        # 初始化模块
        self.camera_handler = CameraHandler()
        self.gesture_recognizer = GestureRecognizer()
        self.mouse_controller = MouseController()
        
        # 初始化变量
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 帧率计算相关变量
        self.frame_count = 0
        self.fps_start_time = cv2.getTickCount()
        self.current_fps = 0
        
        # 镜像模式
        self.mirror_mode = True  # 默认启用镜像
        
        # 手势识别模式
        self.hand_gesture_enabled = False
        
        # 鼠标控制相关
        self.mouse_control_enabled = False  # 鼠标控制开关
        self.right_index_finger_detected_prev = False  # 上一帧是否检测到右手食指
        self.prev_index_tip_x = None  # 上一帧食指尖x坐标
        self.prev_index_tip_y = None  # 上一帧食指尖y坐标
        
        # 创建UI
        self.init_ui()
        
    def init_ui(self):
        # 主中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        # 摄像头选择下拉框
        self.camera_combo = QComboBox()
        self.refresh_cameras_btn = QPushButton("刷新摄像头列表")
        self.refresh_cameras_btn.clicked.connect(self.search_cameras)
        
        # 打开/关闭摄像头按钮
        self.open_close_btn = QPushButton("打开摄像头")
        self.open_close_btn.clicked.connect(self.toggle_camera)
        
        # 镜像模式切换复选框
        self.mirror_checkbox = QCheckBox("镜像模式")
        self.mirror_checkbox.setChecked(self.mirror_mode)
        self.mirror_checkbox.stateChanged.connect(self.toggle_mirror_mode)
        
        # 手势识别切换复选框
        self.hand_gesture_checkbox = QCheckBox("手势识别")
        self.hand_gesture_checkbox.setChecked(False)
        self.hand_gesture_checkbox.stateChanged.connect(self.toggle_hand_gesture)
        
        # 鼠标控制切换复选框
        self.mouse_control_checkbox = QCheckBox("鼠标控制")
        self.mouse_control_checkbox.setChecked(False)
        self.mouse_control_checkbox.stateChanged.connect(self.toggle_mouse_control)
        
        # 添加到控制布局
        control_layout.addWidget(QLabel("摄像头:"))
        control_layout.addWidget(self.camera_combo)
        control_layout.addWidget(self.refresh_cameras_btn)
        control_layout.addWidget(self.open_close_btn)
        control_layout.addWidget(self.mirror_checkbox)
        control_layout.addWidget(self.hand_gesture_checkbox)
        control_layout.addWidget(self.mouse_control_checkbox)
        control_layout.addStretch()
        
        # 摄像头信息显示
        self.camera_info_label = QLabel("未选择摄像头")
        self.camera_info_label.setStyleSheet("font-weight: bold; color: #333; padding: 5px;")
        
        # 视频显示区域
        from constants import VIDEO_LABEL_MIN_WIDTH, VIDEO_LABEL_MIN_HEIGHT
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(VIDEO_LABEL_MIN_WIDTH, VIDEO_LABEL_MIN_HEIGHT)
        self.video_label.setStyleSheet("border: 1px solid gray;")
        
        # 添加布局到主布局
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.camera_info_label)
        main_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        
        # 搜索可用摄像头
        self.search_cameras()
        
        # 连接摄像头选择变化事件
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)

    def search_cameras(self):
        """搜索本地摄像头设备"""
        self.camera_combo.clear()
        
        # 使用摄像头处理器搜索摄像头
        available_cameras, cameras_info = self.camera_handler.search_cameras()
        self.camera_handler.current_camera_info = cameras_info
        
        # 根据摄像头数量为其分配更有意义的名称
        for idx, cam_id in enumerate(available_cameras):
            if len(available_cameras) == 1:
                camera_name = f"内置摄像头 ({cam_id})"
            elif idx == 0:
                camera_name = f"主摄像头 ({cam_id})"
            elif idx == 1:
                camera_name = f"副摄像头 ({cam_id})"
            else:
                camera_name = f"外接摄像头 {idx+1} ({cam_id})"
                
            self.camera_combo.addItem(camera_name, cam_id)
        
        # 如果没有找到摄像头
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("未找到摄像头", -1)
            self.open_close_btn.setEnabled(False)
        else:
            self.open_close_btn.setEnabled(True)
    
    def on_camera_changed(self):
        """当摄像头选择发生变化时更新信息显示"""
        current_index = self.camera_combo.currentIndex()
        if current_index >= 0:
            camera_id = self.camera_combo.currentData()
            if camera_id is not None and camera_id != -1:
                camera_info = self.camera_handler.current_camera_info.get(camera_id)
                if camera_info:
                    self.camera_info_label.setText(f"当前摄像头: {camera_info['name']} (ID: {camera_info['id']})")
                else:
                    self.camera_info_label.setText(f"当前摄像头: 摄像头 {camera_id}")
            else:
                self.camera_info_label.setText("未选择有效摄像头")
        else:
            self.camera_info_label.setText("未选择摄像头")

    def toggle_mirror_mode(self, state):
        """切换镜像模式"""
        self.mirror_mode = bool(state)
    
    def toggle_hand_gesture(self, state):
        """切换手势识别模式"""
        if not self.gesture_recognizer.MEDIAPIPE_AVAILABLE:
            self.hand_gesture_checkbox.setChecked(False)
            return
        self.hand_gesture_enabled = bool(state)
    
    def toggle_mouse_control(self, state):
        """切换鼠标控制模式"""
        # 检查pyautogui是否可用
        try:
            import pyautogui
            pyautogui_available = True
        except ImportError:
            pyautogui_available = False
            
        if not pyautogui_available:
            self.mouse_control_checkbox.setChecked(False)
            return
        self.mouse_control_enabled = bool(state)
        if not self.mouse_control_enabled:
            # 如果禁用鼠标控制，重置跟踪变量
            self.right_index_finger_detected_prev = False
            self.prev_index_tip_x = None
            self.prev_index_tip_y = None
            # Also reset the mouse controller velocity
            self.mouse_controller.reset_velocity()

    def toggle_camera(self):
        """打开或关闭摄像头"""
        if not self.camera_handler.is_opened():
            self.open_camera()
        else:
            self.close_camera()
    
    def open_camera(self):
        """打开摄像头"""
        camera_index = self.camera_combo.currentData()
        if camera_index is None or camera_index == -1:
            return
            
        # 使用摄像头处理器打开摄像头
        if self.camera_handler.open_camera(camera_index):
            # 更新按钮文本
            self.open_close_btn.setText("关闭摄像头")
            
            # 更新摄像头信息显示
            camera_info = self.camera_handler.current_camera_info.get(camera_index)
            if camera_info:
                self.camera_info_label.setText(f"摄像头已开启: {camera_info['name']} (ID: {camera_info['id']})")
            else:
                self.camera_info_label.setText(f"摄像头已开启: 摄像头 {camera_index}")
            
            # 启动定时器来更新帧
            from constants import TIMER_INTERVAL_MS
            self.timer.start(TIMER_INTERVAL_MS)  # 约33 FPS
        else:
            # 显示错误信息
            self.video_label.setText("无法打开摄像头")
            self.camera_info_label.setText("错误：无法打开摄像头")
    
    def close_camera(self):
        """关闭摄像头"""
        self.camera_handler.close_camera()
            
        # 停止定时器
        self.timer.stop()
        
        # 重置帧率计算相关变量
        self.frame_count = 0
        self.fps_start_time = cv2.getTickCount()
        self.current_fps = 0
        
        # 更新按钮文本
        self.open_close_btn.setText("打开摄像头")
        
        # 清空视频显示
        self.video_label.clear()
        self.video_label.setText("摄像头已关闭")
        
        # 更新摄像头信息显示
        self.camera_info_label.setText("摄像头已关闭")
    
    def update_frame(self):
        """更新视频帧"""
        ret, frame = self.camera_handler.read_frame()
        if ret:
            # 如果启用镜像模式，则翻转图像
            if self.mirror_mode:
                frame = cv2.flip(frame, 1)  # 水平翻转
            
            # 如果启用了手势识别且MediaPipe可用，则进行手势检测
            results = None
            if self.hand_gesture_enabled and self.gesture_recognizer.MEDIAPIPE_AVAILABLE:
                # 处理图像以检测手部
                results = self.gesture_recognizer.process_frame(frame)
                
                # 如果检测到手部，则绘制关键点
                if results and results.multi_hand_landmarks:
                    frame = self.gesture_recognizer.draw_landmarks(frame, results)
            
            # 计算帧率
            self.frame_count += 1
            current_time = cv2.getTickCount()
            elapsed_time = (current_time - self.fps_start_time) / cv2.getTickFrequency()
            
            if elapsed_time >= 1.0:  # 每秒更新一次FPS
                self.current_fps = self.frame_count / elapsed_time
                self.frame_count = 0
                self.fps_start_time = current_time
            
            # 在帧上绘制FPS信息
            fps_text = f"FPS: {self.current_fps:.1f}"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 如果启用了手势识别，添加手势识别指示
            if self.hand_gesture_enabled:
                gesture_text = "Hand Gesture: ON"
                cv2.putText(frame, gesture_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                
                # 检测是否只伸出右手食指
                right_index_finger_text = self.gesture_recognizer.detect_right_index_finger_only(results)
                detection_text = f"Right Index Finger: {right_index_finger_text}"
                cv2.putText(frame, detection_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                
                # 检测是否伸出右手食指和中指
                right_index_middle_text = self.gesture_recognizer.detect_right_index_and_middle_fingers(results)
                detection_text2 = f"Right Index+Middle: {right_index_middle_text}"
                cv2.putText(frame, detection_text2, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 1)
                
                # 如果启用了鼠标控制，且检测到只有右手食指伸出，则控制鼠标
                try:
                    import pyautogui
                    pyautogui_available = True
                except ImportError:
                    pyautogui_available = False
                
                if self.mouse_control_enabled and pyautogui_available and right_index_finger_text == "YES":
                    self.control_mouse_with_right_index_finger(results)
                    
                    # 在图像上显示鼠标控制状态
                    mouse_control_text = "Mouse Control: ACTIVE"
                    cv2.putText(frame, mouse_control_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                elif self.mouse_control_enabled:
                    mouse_control_text = "Mouse Control: WAITING"
                    cv2.putText(frame, mouse_control_text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
                
                # 如果检测到食指和中指同时伸出，并且时间间隔满足要求，则执行左键点击
                import time
                current_time = time.time()
                if (pyautogui_available and right_index_middle_text == "YES" and 
                    current_time - self.mouse_controller.last_click_time >= self.mouse_controller.click_interval):
                    self.mouse_controller.left_click()  # 执行左键点击
                    
                    # 在图像上显示点击状态
                    click_text = "Left Click: EXECUTED"
                    cv2.putText(frame, click_text, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
            else:
                gesture_text = "Hand Gesture: OFF"
                cv2.putText(frame, gesture_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
            
            # 将BGR转换为RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 获取图像尺寸
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            
            # 创建QImage
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 调整图像大小以适应标签
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.width(), 
                self.video_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 显示图像
            self.video_label.setPixmap(scaled_pixmap)
        else:
            # 如果读取失败，显示错误消息
            self.video_label.setText("无法读取摄像头数据")
    
    def resizeEvent(self, event):
        """当窗口大小改变时调整图像大小"""
        # 如果摄像头正在运行，重新调整当前帧的大小
        if self.camera_handler.is_opened():
            # 稍微延迟以确保窗口已完全重绘
            QTimer.singleShot(10, self.update_frame)
        super().resizeEvent(event)
    
    def closeEvent(self, event):
        """关闭窗口时释放资源"""
        self.camera_handler.close_camera()
        if self.timer.isActive():
            self.timer.stop()
        event.accept()

    def control_mouse_with_right_index_finger(self, results):
        """使用右手食指控制鼠标"""
        # Get the right index finger position from the gesture recognizer
        finger_pos = self.gesture_recognizer.get_right_index_finger_position(results)
        if finger_pos is None:
            return
        
        # Get screen dimensions
        screen_width, screen_height = self.mouse_controller.screen_width, self.mouse_controller.screen_height
        
        # Convert normalized coordinates to screen coordinates
        screen_x = int(finger_pos[0] * screen_width)
        screen_y = int(finger_pos[1] * screen_height)
        
        # If this is the first frame detecting the right index finger, record initial position
        if not self.right_index_finger_detected_prev:
            self.prev_index_tip_x = screen_x
            self.prev_index_tip_y = screen_y
            self.right_index_finger_detected_prev = True
            # Reset mouse controller velocity
            self.mouse_controller.reset_velocity()
            return
        
        # Calculate movement distance
        dx = screen_x - self.prev_index_tip_x
        dy = screen_y - self.prev_index_tip_y
        
        # Move mouse using the mouse controller
        self.mouse_controller.move_mouse_relative(dx, dy)
        
        # Update previous frame coordinates
        self.prev_index_tip_x = screen_x
        self.prev_index_tip_y = screen_y
        self.right_index_finger_detected_prev = True