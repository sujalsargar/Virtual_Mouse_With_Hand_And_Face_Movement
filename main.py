import cv2
import time
from hand_tracker import HandTracker
from face_tracker import FaceTracker
from gesture_engine import GestureEngine
from mouse_controller import MouseController
from database import get_user

# =====================================================
# MODE SELECTION
# =====================================================

mode = input("Select mode: 1-Automatic  2-Manual : ")

user_name = None

# =====================================================
# AUTOMATIC FACE LOGIN
# =====================================================

if mode == "1":

    from face_auth import load_known_faces, recognize_face

    load_known_faces()

    cap = cv2.VideoCapture(0)

    print("Looking for face...")

    detected_user = None
    stable_frames = 0

    while True:

        success, img = cap.read()

        if not success:
            continue

        img = cv2.flip(img, 1)

        detected_user = recognize_face(img)

        cv2.imshow("Face Login", img)

        if detected_user:

            stable_frames += 1

            if stable_frames >= 3:
                user_name = detected_user.strip().lower()
                print("User detected:", user_name)
                break

        else:
            stable_frames = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            exit()

    cap.release()
    cv2.destroyAllWindows()

# =====================================================
# MANUAL LOGIN
# =====================================================

elif mode == "2":

    user_name = input("Enter user name: ").strip().lower()

else:
    print("Invalid mode")
    exit()

# =====================================================
# LOAD USER SETTINGS
# =====================================================

user = get_user(user_name)

if user is None:
    print("User not found in database:", user_name)
    exit()

print("Starting gesture control for:", user_name)

blink_threshold = user[4]
scroll_speed = user[5]

# =====================================================
# INITIALIZE
# =====================================================

cap = cv2.VideoCapture(0)

hand_tracker = HandTracker()
face_tracker = FaceTracker()
gesture_engine = GestureEngine()
mouse = MouseController()

current_mode = "HAND"

blink_start_time = None
short_blink = 0.15
long_blink = 0.5

prev_hand_y = None
scroll_velocity = 0

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    success, img = cap.read()

    if not success:
        continue

    img = cv2.flip(img, 1)

    h, w, _ = img.shape

    # =====================================================
    # HAND MODE
    # =====================================================

    if current_mode == "HAND":

        img, hand_landmarks = hand_tracker.process_frame(img)

        if hand_landmarks:

            gesture, _ = gesture_engine.detect_gesture(
                hand_landmarks, img.shape
            )

            index_tip = hand_landmarks.landmark[8]

            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            mouse.move_absolute(x, y, w, h)

            if gesture != "Scroll":
                prev_hand_y = None
                scroll_velocity = 0
                mouse.reset_scroll()

            if gesture == "Left Click":
                time.sleep(0.03)
                mouse.left_click()

            elif gesture == "Double Click":
                time.sleep(0.03)
                mouse.left_click()
                mouse.left_click()

            elif gesture == "Right Click":
                mouse.right_click()

            elif gesture == "Dragging":
                mouse.start_drag()

            elif gesture == "Release":
                mouse.release_drag()

            elif gesture == "Scroll":

                hand_y = index_tip.y

                if prev_hand_y is not None:

                    raw_delta = prev_hand_y - hand_y

                    if abs(raw_delta) > 0.003:

                        smooth_delta = 0.7 * raw_delta

                        scroll_velocity = (
                            0.8 * scroll_velocity +
                            smooth_delta * scroll_speed
                        )

                        scroll_velocity = max(min(scroll_velocity, 50), -50)

                        mouse.smooth_scroll(scroll_velocity)

                prev_hand_y = hand_y

    # =====================================================
    # FACE MODE
    # =====================================================

    else:

        img, face_landmarks = face_tracker.process_frame(img)

        if face_landmarks:

            nose = face_landmarks.landmark[1]

            x = int(nose.x * w)
            y = int(nose.y * h)

            mouse.move_absolute(x, y, w, h)

            left_eye, right_eye = face_tracker.get_blink_ratio(
                face_landmarks
            )

            avg_eye = (left_eye + right_eye) / 2

            eye_closed = avg_eye < blink_threshold

            current_time = time.time()

            if eye_closed:

                if blink_start_time is None:
                    blink_start_time = current_time

            else:

                if blink_start_time is not None:

                    duration = current_time - blink_start_time

                    if short_blink < duration < long_blink:
                        mouse.left_click()

                    elif duration >= long_blink:
                        mouse.right_click()

                    blink_start_time = None

            tilt = face_tracker.get_head_tilt(face_landmarks)

            if abs(tilt) > 0.01:
                mouse.smooth_scroll(tilt * scroll_speed)
            else:
                mouse.reset_scroll()

    # =====================================================
    # UI
    # =====================================================

    cv2.putText(
        img,
        f"Mode: {current_mode}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.imshow("AirClick Pro - Hybrid", img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('h'):
        current_mode = "HAND"
        mouse.reset_scroll()

    elif key == ord('f'):
        current_mode = "FACE"
        mouse.reset_scroll()

cap.release()
cv2.destroyAllWindows()