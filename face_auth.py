import face_recognition
import cv2
import os
import numpy as np

known_encodings = []
known_names = []


def load_known_faces():

    for file in os.listdir("user_images"):

        path = os.path.join("user_images", file)

        image = face_recognition.load_image_file(path)

        encodings = face_recognition.face_encodings(image)

        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(file.split(".")[0])

    print("Loaded users:", known_names)


def recognize_face(frame):

    # Resize frame for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert BGR → RGB
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect face locations
    face_locations = face_recognition.face_locations(rgb_small)

    if len(face_locations) == 0:
        return None

    # Encode detected faces
    encodings = face_recognition.face_encodings(rgb_small, face_locations)

    if len(encodings) == 0:
        return None

    for encoding in encodings:

        # Compute distance to all known faces
        face_distances = face_recognition.face_distance(known_encodings, encoding)

        # Find best match
        best_match_index = np.argmin(face_distances)

        # Check if match is close enough
        if face_distances[best_match_index] < 0.5:
            return known_names[best_match_index]

    return None