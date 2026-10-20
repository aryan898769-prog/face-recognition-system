import cv2
import numpy as np


def image_to_embedding(image: np.ndarray) -> np.ndarray:
    """Create a compact face signature from the image using OpenCV."""
    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    if image.shape[2] == 4:
        image = image[:, :, :3]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64))
    hist = cv2.calcHist([gray], [0], None, [16], [0, 256]).flatten()
    hist = hist / (hist.sum() + 1e-8)
    return hist.astype(np.float32)
