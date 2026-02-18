import pyautogui
import numpy as np

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class MouseController:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

        self.prev_x = None
        self.prev_y = None

        self.prev_scroll = None

        # Movement tuning
        self.dead_zone = 2          # remove micro shaking
        self.edge_zone = 40         # easier corner reach
        self.scroll_sensitivity = 200  # stronger scroll

    # ------------------------------------------------
    # Real Absolute Mapping (Smooth + Stable)
    # ------------------------------------------------
    def move_absolute(self, x, y, frame_w, frame_h):

        # Map camera frame → screen
        screen_x = np.interp(x, [0, frame_w], [0, self.screen_width])
        screen_y = np.interp(y, [0, frame_h], [0, self.screen_height])

        # First frame protection
        if self.prev_x is None:
            self.prev_x = screen_x
            self.prev_y = screen_y
            pyautogui.moveTo(screen_x, screen_y)
            return

        dx = screen_x - self.prev_x
        dy = screen_y - self.prev_y

        # Remove tiny movement jitter
        if abs(dx) < self.dead_zone:
            dx = 0
        if abs(dy) < self.dead_zone:
            dy = 0

        velocity = np.hypot(dx, dy)

        # Dynamic smoothing
        if velocity < 10:
            alpha = 0.12
        elif velocity < 40:
            alpha = 0.22
        else:
            alpha = 0.35

        curr_x = alpha * screen_x + (1 - alpha) * self.prev_x
        curr_y = alpha * screen_y + (1 - alpha) * self.prev_y

        # Edge boost (helps reach corners)
        if x < self.edge_zone:
            curr_x *= 1.05
        if x > frame_w - self.edge_zone:
            curr_x *= 1.05
        if y < self.edge_zone:
            curr_y *= 1.05
        if y > frame_h - self.edge_zone:
            curr_y *= 1.05

        # Clamp to screen
        curr_x = max(0, min(self.screen_width - 1, curr_x))
        curr_y = max(0, min(self.screen_height - 1, curr_y))

        pyautogui.moveTo(curr_x, curr_y)

        self.prev_x = curr_x
        self.prev_y = curr_y

    # ------------------------------------------------
    # Real Scroll (Strong + Stable)
    # ------------------------------------------------
    def smooth_scroll(self, current_value):

        if self.prev_scroll is None:
            self.prev_scroll = current_value
            return

        delta = self.prev_scroll - current_value

        # Ignore tiny tilt noise
        if abs(delta) < 0.002:
            return

        scroll_amount = int(delta * self.scroll_sensitivity)

        pyautogui.scroll(scroll_amount)

        self.prev_scroll = current_value

    def reset_scroll(self):
        self.prev_scroll = None

    # ------------------------------------------------
    # Clicks
    # ------------------------------------------------
    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.rightClick()
