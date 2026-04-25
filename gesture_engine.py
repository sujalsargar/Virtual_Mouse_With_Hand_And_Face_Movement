import time
import numpy as np
from config import *


class GestureEngine:

    def __init__(self):

        # Drag state
        self.dragging = False
        self.pinch_start_time = None

        # Click timing
        self.last_click_time = 0
        self.last_pinch_time = 0

        # Settings
        self.double_click_threshold = 0.3
        self.paused = False

    # ------------------------------------------------
    # Distance between two landmarks
    # ------------------------------------------------
    def get_distance(self, p1, p2, w, h):

        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)

        return np.hypot(x2 - x1, y2 - y1)

    # ------------------------------------------------
    # Finger up detection
    # ------------------------------------------------
    def is_finger_up(self, tip, pip):
        return tip.y < pip.y

    # ------------------------------------------------
    # Main gesture detection
    # ------------------------------------------------
    def detect_gesture(self, landmarks, frame_shape):

        if landmarks is None:
            return "None", {}

        h, w, _ = frame_shape
        lm = landmarks.landmark

        # Fingertips
        index_tip = lm[8]
        middle_tip = lm[12]
        ring_tip = lm[16]
        pinky_tip = lm[20]
        thumb_tip = lm[4]

        # Finger joints
        index_pip = lm[6]
        middle_pip = lm[10]
        ring_pip = lm[14]
        pinky_pip = lm[18]

        # ------------------------------------------------
        # Finger states
        # ------------------------------------------------
        index_up = self.is_finger_up(index_tip, index_pip)
        middle_up = self.is_finger_up(middle_tip, middle_pip)
        ring_up = self.is_finger_up(ring_tip, ring_pip)
        pinky_up = self.is_finger_up(pinky_tip, pinky_pip)

        # ------------------------------------------------
        # Distance calculations
        # ------------------------------------------------
        pinch_index = self.get_distance(index_tip, thumb_tip, w, h)
        pinch_middle = self.get_distance(middle_tip, thumb_tip, w, h)

        current_time = time.time()

        # ------------------------------------------------
        # PAUSE (Open palm)
        # ------------------------------------------------
        if index_up and middle_up and ring_up and pinky_up:
            self.paused = True
            return "Pause", {}

        self.paused = False

        # ------------------------------------------------
        # INDEX PINCH (Click / Drag)
        # ------------------------------------------------
        if pinch_index < CLICK_THRESHOLD:

            if self.pinch_start_time is None:
                self.pinch_start_time = current_time

            pinch_duration = current_time - self.pinch_start_time

            # Start drag
            if pinch_duration > DRAG_HOLD_TIME and not self.dragging:
                self.dragging = True
                return "Dragging", {}

        else:

            if self.pinch_start_time is not None:

                pinch_duration = current_time - self.pinch_start_time
                self.pinch_start_time = None

                # Release drag
                if self.dragging:
                    self.dragging = False
                    return "Release", {}

                # Quick pinch = click
                if pinch_duration < DRAG_HOLD_TIME:

                    # Double click detection
                    if current_time - self.last_pinch_time < self.double_click_threshold:

                        if current_time - self.last_click_time > CLICK_COOLDOWN:
                            self.last_click_time = current_time
                            self.last_pinch_time = 0
                            return "Double Click", {}

                    # Single click
                    if current_time - self.last_click_time > CLICK_COOLDOWN:
                        self.last_click_time = current_time
                        self.last_pinch_time = current_time
                        return "Left Click", {}

        # ------------------------------------------------
        # RIGHT CLICK (Thumb + Middle pinch)
        # ------------------------------------------------
        if pinch_middle < CLICK_THRESHOLD:

            if current_time - self.last_click_time > CLICK_COOLDOWN:
                self.last_click_time = current_time
                return "Right Click", {}

        # ------------------------------------------------
        # SCROLL (Index + Middle up)
        # ------------------------------------------------
        if index_up and middle_up and not ring_up and not pinky_up:
            return "Scroll", {}

        # ------------------------------------------------
        # Default movement
        # ------------------------------------------------
        return "Move", {}