import fitz
import cv2
import numpy as np
from PIL import Image


def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []

    for page in doc:
        pix = page.get_pixmap(
            matrix=fitz.Matrix(4, 4)
        )

        img = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        img = cv2.cvtColor(
            np.array(img),
            cv2.COLOR_RGB2BGR
        )

        images.append(img)

    doc.close()
    return images