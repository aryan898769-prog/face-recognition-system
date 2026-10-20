import os
import pickle
from typing import List

import cv2
import numpy as np
from app.face_model import image_to_embedding
from app.database import get_all_employees

EMPLOYEE_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "employees")
ENCODINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "encodings.pkl")
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def crop_largest_face(image: np.ndarray) -> np.ndarray | None:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
    return image[y : y + h, x : x + w]


def load_employee_images(employee_id: str) -> List[str]:
    employee_dir = os.path.join(EMPLOYEE_IMAGES_DIR, employee_id)
    if not os.path.isdir(employee_dir):
        return []
    return [os.path.join(employee_dir, f) for f in os.listdir(employee_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]


def generate_embeddings():
    """Generate embeddings for all registered employees using pretrained model."""
    employees = get_all_employees()
    employee_embeddings = {}

    print("Generating embeddings from pretrained model...")
    for employee in employees:
        image_paths = load_employee_images(employee.employee_id)
        if not image_paths:
            print(f"No images found for {employee.name} ({employee.employee_id})")
            continue
        
        print(f"\nProcessing {employee.name} ({employee.employee_id})...")
        embeddings = []
        for idx, image_path in enumerate(image_paths):
            image = cv2.imread(image_path)
            if image is None:
                print(f"  ✗ Failed to load image {image_path}")
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_image = crop_largest_face(image)
            if face_image is None:
                print(f"  ✗ No face detected in {image_path}")
                continue
            try:
                embedding = image_to_embedding(face_image)
            except Exception as exc:
                print(f"  ✗ Encoding failed for {image_path}: {exc}")
                continue
            embeddings.append(embedding)
            print(f"  ✓ Image {idx+1}: embedding extracted (shape: {embedding.shape})")
        
        if embeddings:
            avg_embedding = np.mean(embeddings, axis=0)
            employee_embeddings[employee.employee_id] = avg_embedding
            print(f"✓ Generated embedding for {employee.name} from {len(embeddings)} image(s)")
            print(f"  Embedding mean: {np.mean(avg_embedding):.4f}, std: {np.std(avg_embedding):.4f}")
        else:
            print(f"✗ No valid embeddings generated for {employee.name}")

    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(employee_embeddings, f)

    print(f"\n✓ Saved embeddings for {len(employee_embeddings)} employees to {ENCODINGS_FILE}")



if __name__ == "__main__":
    generate_embeddings()
