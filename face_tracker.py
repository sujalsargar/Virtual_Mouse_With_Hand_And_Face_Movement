import cv2
import mediapipe as mp


class FaceTracker:
    def __init__(self):

        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, img):

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        landmarks = None

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_draw.draw_landmarks(
                    img,
                    face_landmarks,
                    self.mp_face.FACEMESH_CONTOURS
                )
                landmarks = face_landmarks

        return img, landmarks

    def get_blink_ratio(self, landmarks):
        left_top = landmarks.landmark[159]
        left_bottom = landmarks.landmark[145]
        right_top = landmarks.landmark[386]
        right_bottom = landmarks.landmark[374]

        left_distance = abs(left_top.y - left_bottom.y)
        right_distance = abs(right_top.y - right_bottom.y)

        return left_distance, right_distance

    def get_head_tilt(self, landmarks):
        left_eye_corner = landmarks.landmark[33]
        right_eye_corner = landmarks.landmark[263]
        return left_eye_corner.y - right_eye_corner.y
