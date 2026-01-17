"""手势识别模块，负责使用MediaPipe进行手部检测和手势识别"""

import cv2
import math
import time
from constants import HAND_DETECTION_CONFIDENCE, HAND_TRACKING_CONFIDENCE, MAX_NUM_HANDS


class GestureRecognizer:
    """手势识别器类，负责手势检测和识别"""
    
    def __init__(self):
        # 尝试导入MediaPipe用于手势识别
        try:
            from mediapipe.python.solutions import hands
            from mediapipe.python.solutions import drawing_utils
            from mediapipe.python.solutions import drawing_styles
            self.mp_hands = hands
            self.mp_drawing = drawing_utils
            self.mp_drawing_styles = drawing_styles
            self.MEDIAPIPE_AVAILABLE = True
            
            # 初始化手部检测器
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=MAX_NUM_HANDS,
                min_detection_confidence=HAND_DETECTION_CONFIDENCE,
                min_tracking_confidence=HAND_TRACKING_CONFIDENCE
            )
        except ImportError:
            self.MEDIAPIPE_AVAILABLE = False
            self.mp_hands = None
            self.mp_drawing = None
            self.mp_drawing_styles = None
            self.hands = None
            print("MediaPipe未安装，手势识别功能将不可用")
    
    def process_frame(self, frame):
        """处理图像帧以检测手部"""
        if not self.MEDIAPIPE_AVAILABLE or self.hands is None:
            return None
        
        # 将BGR图像转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像以检测手部
        results = self.hands.process(rgb_frame)
        return results
    
    def draw_landmarks(self, frame, results):
        """在图像上绘制手部关键点"""
        if not self.MEDIAPIPE_AVAILABLE or not results.multi_hand_landmarks:
            return frame
        
        for hand_landmarks in results.multi_hand_landmarks:
            # 绘制手部关键点
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        return frame
    
    def detect_right_index_finger_only(self, results):
        """检测是否只伸出右手食指"""
        if not self.MEDIAPIPE_AVAILABLE or not results.multi_hand_landmarks or not results.multi_handedness:
            return "NO"
        
        # 查找右手
        right_hand_landmarks = None
        right_hand_index = -1
        
        for i, handedness in enumerate(results.multi_handedness):
            if handedness.classification[0].label == "Right":
                right_hand_landmarks = results.multi_hand_landmarks[i]
                right_hand_index = i
                break
        
        if right_hand_landmarks is None:
            return "NO"
        
        # 获取右手关键点
        landmarks = right_hand_landmarks.landmark
        
        # 获取各个手指关键点
        index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
        index_dip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_DIP.value]
        middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value]
        middle_dip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_DIP.value]
        ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP.value]
        ring_dip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_DIP.value]
        pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP.value]
        pinky_dip = landmarks[self.mp_hands.HandLandmark.PINKY_DIP.value]
        thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP.value]
        thumb_ip = landmarks[self.mp_hands.HandLandmark.THUMB_IP.value]
        
        wrist = landmarks[self.mp_hands.HandLandmark.WRIST.value]
        
        # 判断食指是否伸直（指尖y坐标小于第二关节y坐标，即更靠近图像顶部）
        index_extended = index_tip.y < index_dip.y
        
        # 判断其他手指是否弯曲（指尖y坐标大于第二关节y坐标，即更靠近图像底部）
        middle_bent = middle_tip.y > middle_dip.y
        ring_bent = ring_tip.y > ring_dip.y
        pinky_bent = pinky_tip.y > pinky_dip.y
        
        # 拇指判断：当拇指伸直时，其tip会远离手腕；弯曲时会靠近手腕
        # 计算拇指tip到手腕的距离，以及thumb_ip到手腕的距离
        thumb_distance = math.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)
        thumb_ip_distance = math.sqrt((thumb_ip.x - wrist.x)**2 + (thumb_ip.y - wrist.y)**2)
        
        # 拇指弯曲：thumb tip相对靠近手腕
        thumb_bent = thumb_distance < thumb_ip_distance * 1.2  # 乘以系数允许一些变化
        
        # 综合判断：只有食指伸直，其他手指弯曲
        if index_extended and middle_bent and ring_bent and pinky_bent and thumb_bent:
            return "YES"
        else:
            return "NO"
    
    def detect_right_index_and_middle_fingers(self, results):
        """检测是否伸出右手食指和中指"""
        if not self.MEDIAPIPE_AVAILABLE or not results.multi_hand_landmarks or not results.multi_handedness:
            return "NO"
        
        # 查找右手
        right_hand_landmarks = None
        right_hand_index = -1
        
        for i, handedness in enumerate(results.multi_handedness):
            if handedness.classification[0].label == "Right":
                right_hand_landmarks = results.multi_hand_landmarks[i]
                right_hand_index = i
                break
        
        if right_hand_landmarks is None:
            return "NO"
        
        # 获取右手关键点
        landmarks = right_hand_landmarks.landmark
        
        # 获取各个手指关键点
        index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
        index_dip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_DIP.value]
        middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value]
        middle_dip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_DIP.value]
        ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP.value]
        ring_dip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_DIP.value]
        pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP.value]
        pinky_dip = landmarks[self.mp_hands.HandLandmark.PINKY_DIP.value]
        thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP.value]
        thumb_ip = landmarks[self.mp_hands.HandLandmark.THUMB_IP.value]
        
        wrist = landmarks[self.mp_hands.HandLandmark.WRIST.value]
        
        # 判断食指和中指是否伸直（指尖y坐标小于第二关节y坐标，即更靠近图像顶部）
        index_extended = index_tip.y < index_dip.y
        middle_extended = middle_tip.y < middle_dip.y
        
        # 判断其他手指是否弯曲（指尖y坐标大于第二关节y坐标，即更靠近图像底部）
        ring_bent = ring_tip.y > ring_dip.y
        pinky_bent = pinky_tip.y > pinky_dip.y
        
        # 拇指判断：当拇指伸直时，其tip会远离手腕；弯曲时会靠近手腕
        thumb_distance = math.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2)
        thumb_ip_distance = math.sqrt((thumb_ip.x - wrist.x)**2 + (thumb_ip.y - wrist.y)**2)
        
        # 拇指弯曲：thumb tip相对靠近手腕
        thumb_bent = thumb_distance < thumb_ip_distance * 1.2  # 乘以系数允许一些变化
        
        # 综合判断：食指和中指伸直，其他手指弯曲
        if index_extended and middle_extended and ring_bent and pinky_bent and thumb_bent:
            return "YES"
        else:
            return "NO"
    
    def get_right_index_finger_position(self, results):
        """获取右手食指尖的位置坐标"""
        if not self.MEDIAPIPE_AVAILABLE or not results.multi_hand_landmarks or not results.multi_handedness:
            return None
        
        # 查找右手
        right_hand_landmarks = None
        for i, handedness in enumerate(results.multi_handedness):
            if handedness.classification[0].label == "Right":
                right_hand_landmarks = results.multi_hand_landmarks[i]
                break
        
        if right_hand_landmarks is None:
            return None
        
        # 获取右手食指尖坐标
        landmarks = right_hand_landmarks.landmark
        index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
        return index_tip.x, index_tip.y