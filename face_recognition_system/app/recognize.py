import os
import pickle
import sys
from datetime import datetime

import cv2
import numpy as np

from app.access_control import check_access, log_access, notify_admin
from app.database import get_employee_by_id
from app.face_model import image_to_embedding

ENCODINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "encodings.pkl")
TOLERANCE = 0.45


def detect_faces(image: np.ndarray):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return [(y, x + w, y + h, x) for x, y, w, h in faces]


def load_employee_embeddings():
    """Load precomputed employee embeddings."""
    if not os.path.isfile(ENCODINGS_FILE):
        raise FileNotFoundError("Embeddings file not found. Run train.py first.")
    with open(ENCODINGS_FILE, "rb") as f:
        return pickle.load(f)


def recognize_from_camera(area: str = "Lobby"):
    employee_embeddings = load_employee_embeddings()
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        raise RuntimeError("Could not open camera")

    print(f"Starting recognition for area: {area}")
    print(f"Loaded {len(employee_embeddings)} employee profiles")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = frame[:, :, ::-1]
        detections = detect_faces(rgb_frame)

        for top, right, bottom, left in detections:
            face_image = rgb_frame[top:bottom, left:right]
            if face_image.size == 0:
                continue

            current_embedding = image_to_embedding(face_image)

            best_match_id = None
            best_distance = float("inf")

            for emp_id, emp_embedding in employee_embeddings.items():
                distance = np.linalg.norm(current_embedding - emp_embedding)
                if distance < best_distance:
                    best_distance = distance
                    best_match_id = emp_id

            match_found = best_distance <= TOLERANCE

            if match_found:
                allowed, name = check_access(best_match_id, area)
                log_access(best_match_id, area, name, allowed)
                if not allowed:
                    notify_admin(best_match_id, name, area)
                label = f"{name} (dist: {best_distance:.2f}) {'OK' if allowed else 'DENIED'}"
                print(f"{name} recognized (distance: {best_distance:.3f})")
            else:
                print(f"Unknown person detected (distance: {best_distance:.3f}) at {datetime.utcnow().isoformat()}")
                label = f"Unknown (dist: {best_distance:.2f})"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    area = sys.argv[1] if len(sys.argv) > 1 else "Lobby"
    recognize_from_camera(area)
