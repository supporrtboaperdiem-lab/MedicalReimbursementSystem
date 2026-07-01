import cv2


def image_to_array(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Unable to read image file: {image_path}")

    return image