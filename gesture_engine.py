import time
import numpy as np
from config import *

class GestureEngine:
    def __init__(self):
        self.last_click_time = 0
        self.dragging = False
        self.pinch_start_time = 0
        self.paused = False

        # NEW: Double Click Support
        self.last_pinch_time = 0
        self.double_click_threshold = 0.3  # seconds

    def get_distance(self, p1, p2, w, h):
        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)
        return np.hypot(x2 - x1, y2 - y1)

    def is_finger_up(self, tip, pip):
        return tip.y < pip.y

    def detect_gesture(self, landmarks, frame_shape):
        if landmarks is None:
            return "None", {}

        h, w, _ = frame_shape
        lm = landmarks.landmark

        index_tip = lm[8]
        middle_tip = lm[12]
        ring_tip = lm[16]
        pinky_tip = lm[20]
        thumb_tip = lm[4]

        index_pip = lm[6]
        middle_pip = lm[10]
        ring_pip = lm[14]
        pinky_pip = lm[18]

        # Finger states
        index_up = self.is_finger_up(index_tip, index_pip)
        middle_up = self.is_finger_up(middle_tip, middle_pip)
        ring_up = self.is_finger_up(ring_tip, ring_pip)
        pinky_up = self.is_finger_up(pinky_tip, pinky_pip)

        # Distances
        pinch_index = self.get_distance(index_tip, thumb_tip, w, h)
        pinch_middle = self.get_distance(middle_tip, thumb_tip, w, h)

        current_time = time.time()

        # -------------------------
        # PAUSE (Open Palm)
        # -------------------------
        if index_up and middle_up and ring_up and pinky_up:
            self.paused = True
            return "Pause", {"paused": True}

        self.paused = False

        # -------------------------
        # LEFT CLICK + DOUBLE CLICK + DRAG
        # -------------------------
        if pinch_index < CLICK_THRESHOLD:

            if current_time - self.last_click_time > CLICK_COOLDOWN:

                # Double Click Detection
                if current_time - self.last_pinch_time < self.double_click_threshold:
                    self.last_pinch_time = 0
                    self.last_click_time = current_time
                    return "Double Click", {}

                # Normal Left Click
                self.last_pinch_time = current_time
                self.last_click_time = current_time
                self.pinch_start_time = current_time
                return "Left Click", {}

            # Drag Detection
            if current_time - self.pinch_start_time > DRAG_HOLD_TIME:
                self.dragging = True
                return "Dragging", {"drag": True}

        else:
            if self.dragging:
                self.dragging = False
                return "Release", {"release": True}

        # -------------------------
        # RIGHT CLICK
        # -------------------------
        if pinch_middle < CLICK_THRESHOLD:
            if current_time - self.last_click_time > CLICK_COOLDOWN:
                self.last_click_time = current_time
                return "Right Click", {}

        # -------------------------
        # SCROLL
        # -------------------------
        if index_up and middle_up and not ring_up:
            return "Scroll", {"scroll": True}

        return "Move", {}
