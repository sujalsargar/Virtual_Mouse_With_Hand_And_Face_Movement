import cv2
import time
from hand_tracker import HandTracker
from face_tracker import FaceTracker
from gesture_engine import GestureEngine
from mouse_controller import MouseController


def main():

    cap = cv2.VideoCapture(0)

    hand_tracker = HandTracker()
    face_tracker = FaceTracker()
    gesture_engine = GestureEngine()
    mouse = MouseController()

    current_mode = "HAND"

    # Blink system
    blink_start_time = None
    blink_threshold = 0.012
    short_blink = 0.15
    long_blink = 0.5

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

                # Absolute movement (real mouse feel)
                index_tip = hand_landmarks.landmark[8]
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)

                mouse.move_absolute(x, y, w, h)

                if gesture == "Left Click":
                    mouse.left_click()

                elif gesture == "Right Click":
                    mouse.right_click()

        # =====================================================
        # FACE MODE
        # =====================================================
        else:

            img, face_landmarks = face_tracker.process_frame(img)

            if face_landmarks:

                # Absolute face movement
                nose = face_landmarks.landmark[1]
                x = int(nose.x * w)
                y = int(nose.y * h)

                mouse.move_absolute(x, y, w, h)

                # Blink click (stable)
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

                # Smooth head tilt scroll
                tilt = face_tracker.get_head_tilt(face_landmarks)
                mouse.smooth_scroll(tilt)

        # =====================================================
        # DISPLAY
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
            print("Switched to HAND")
        elif key == ord('f'):
            current_mode = "FACE"
            mouse.reset_scroll()
            print("Switched to FACE")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
