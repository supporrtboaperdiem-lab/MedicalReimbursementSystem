import cv2
import numpy as np


def deskew(image, max_allowed_angle=10):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    coords = np.column_stack(np.where(thresh > 0))

    if len(coords) < 100:
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    angle = -angle

    # Important safety rule:
    # Only correct small slants, not pages that OpenCV thinks are 90 degrees.
    if abs(angle) > max_allowed_angle:
        return image

    if abs(angle) < 0.3:
        return image

    h, w = image.shape[:2]

    matrix = cv2.getRotationMatrix2D(
        (w // 2, h // 2),
        angle,
        1.0
    )

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated