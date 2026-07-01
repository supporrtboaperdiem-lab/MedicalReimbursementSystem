import re

from app.services.ocr.constants import NUMBER_PATTERN


def is_valid_numeric_line(line):
    if not re.search(NUMBER_PATTERN, line):
        return False

    alpha_count = sum(c.isalpha() for c in line)

    if alpha_count < 3:
        return False

    return True