import pyautogui
import time
import math
from constants import MOUSE_SMOOTH_FACTOR, MOUSE_MAX_VELOCITY, CLICK_INTERVAL, \
    SMALL_MOVEMENT_THRESHOLD, MEDIUM_MOVEMENT_THRESHOLD, \
    SMALL_MOVEMENT_SENSITIVITY, MEDIUM_MOVEMENT_SENSITIVITY, BASE_LARGE_MOVEMENT_SENSITIVITY


class MouseController:
    """鼠标控制器类，负责鼠标移动和点击操作"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True  # 启用安全模式
        self.screen_width, self.screen_height = pyautogui.size()
        
        # 鼠标移动平滑处理
        self.smooth_factor = MOUSE_SMOOTH_FACTOR  # 平滑因子，越小越平滑
        self.velocity_x = 0  # x轴速度
        self.velocity_y = 0  # y轴速度
        self.max_velocity = MOUSE_MAX_VELOCITY  # 最大速度限制，增加以支持更大范围移动
        
        # 左键点击控制
        self.last_click_time = 0  # 上次点击时间
        self.click_interval = CLICK_INTERVAL  # 点击间隔时间（秒）
    
    def move_mouse_relative(self, dx, dy):
        """相对移动鼠标"""
        # 使用平方函数来增强大动作的灵敏度，同时保持小动作的精确性
        # 当手势移动距离较大时，应用更高的放大倍数
        magnitude = math.sqrt(dx*dx + dy*dy)
        
        if magnitude > 0:
            # 计算缩放比例，对大动作进行放大
            if magnitude < SMALL_MOVEMENT_THRESHOLD:
                # 小幅度移动，保持精细控制
                scale_factor = SMALL_MOVEMENT_SENSITIVITY  # 提高小移动的灵敏度
            elif magnitude < MEDIUM_MOVEMENT_THRESHOLD:
                # 中等幅度移动
                scale_factor = MEDIUM_MOVEMENT_SENSITIVITY
            else:
                # 大幅度移动，应用更高放大率
                scale_factor = BASE_LARGE_MOVEMENT_SENSITIVITY + (magnitude - MEDIUM_MOVEMENT_THRESHOLD) * 0.5  # 随距离增加而增加灵敏度
        
            # 计算调整后的移动量
            adjusted_dx = dx * scale_factor
            adjusted_dy = dy * scale_factor
        else:
            adjusted_dx = 0
            adjusted_dy = 0
        
        # 使用加速度和速度的物理模型来平滑移动
        # 计算目标速度
        target_velocity_x = adjusted_dx
        target_velocity_y = adjusted_dy
        
        # 限制最大速度，防止过度快速移动
        max_speed = self.max_velocity
        target_velocity_x = max(-max_speed, min(max_speed, target_velocity_x))
        target_velocity_y = max(-max_speed, min(max_speed, target_velocity_y))
        
        # 平滑过渡到目标速度
        self.velocity_x = self.smooth_factor * target_velocity_x + (1 - self.smooth_factor) * self.velocity_x
        self.velocity_y = self.smooth_factor * target_velocity_y + (1 - self.smooth_factor) * self.velocity_y
        
        # 执行相对鼠标移动
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            pyautogui.moveRel(int(self.velocity_x), int(self.velocity_y))
    
    def reset_velocity(self):
        """重置鼠标移动速度"""
        self.velocity_x = 0
        self.velocity_y = 0
    
    def left_click(self):
        """执行左键点击"""
        current_time = time.time()
        if current_time - self.last_click_time >= self.click_interval:
            pyautogui.click()  # 执行左键点击
            self.last_click_time = current_time  # 更新上次点击时间
            return True
        return False