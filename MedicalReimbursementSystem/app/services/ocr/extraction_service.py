import os
from pathlib import Path

import cv2

from app.services.ocr.constants import DEBUG_OCR_FOLDER, SUPPORTED_OCR_EXTENSIONS
from app.services.ocr.image_loader import image_to_array
from app.services.ocr.image_preprocessor import deskew
from app.services.ocr.line_filter import is_valid_numeric_line
from app.services.ocr.line_merger import merge_same_line
from app.services.ocr.paddle_engine import PaddleEngine
from app.services.ocr.pdf_renderer import pdf_to_images


def extract_numeric_lines(file_path, save_debug_pages=True):
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_OCR_EXTENSIONS:
        raise ValueError(f"Unsupported OCR file type: {extension}")

    if extension == ".pdf":
        pages = pdf_to_images(str(file_path))
    else:
        pages = [image_to_array(str(file_path))]

    output = []
    line_counter = 1

    if save_debug_pages:
        os.makedirs(DEBUG_OCR_FOLDER, exist_ok=True)

    for page_num, page_img in enumerate(pages, start=1):
        try:
            page_img = deskew(page_img)

            if save_debug_pages:
                debug_path = os.path.join(
                    DEBUG_OCR_FOLDER,
                    f"{file_path.stem}_page_{page_num}.png"
                )
                cv2.imwrite(debug_path, page_img)

            result = PaddleEngine.recognize(page_img)

            if not result or not result[0]:
                continue

            merged_lines = merge_same_line(result[0])

            for line_data in merged_lines:
                line = line_data["text"]

                if not is_valid_numeric_line(line):
                    continue

                record = {
                    "line_no": line_counter,
                    "page": page_num,
                    "text": line,
                    "confidence": round(line_data["confidence"], 4),
                    "source_file": file_path.name
                }

                output.append(record)
                line_counter += 1

        except Exception as e:
            output.append({
                "line_no": None,
                "page": page_num,
                "text": None,
                "source_file": file_path.name,
                "error": str(e)
            })

    return output