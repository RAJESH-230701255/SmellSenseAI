import cv2
import numpy as np

def detect_spoilage(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower = np.array([0, 0, 0])
    upper = np.array([180, 255, 50])

    mask = cv2.inRange(hsv, lower, upper)

    spoil_ratio = np.sum(mask > 0) / mask.size

    return spoil_ratio > 0.2