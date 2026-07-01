def _box_stats(box):
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]

    return {
        "x_min": min(xs),
        "x_max": max(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "x_center": sum(xs) / len(xs),
        "y_center": sum(ys) / len(ys),
        "height": max(ys) - min(ys),
        "width": max(xs) - min(xs),
    }


def normalize_ocr_items(ocr_result, min_confidence=0.30):
    items = []

    for item in ocr_result:
        box = item[0]
        text = item[1][0]
        confidence = item[1][1]

        if not text or confidence < min_confidence:
            continue

        stats = _box_stats(box)

        items.append({
            "text": text.strip(),
            "confidence": confidence,
            **stats,
        })

    return items


def _vertical_overlap(a, b):
    top = max(a["y_min"], b["y_min"])
    bottom = min(a["y_max"], b["y_max"])

    overlap = max(0, bottom - top)

    min_height = max(1, min(a["height"], b["height"]))

    return overlap / min_height


def group_items_into_rows(items, overlap_threshold=0.35):
    if not items:
        return []

    items = sorted(items, key=lambda x: x["y_center"])

    rows = []

    for item in items:
        placed = False

        for row in rows:
            row_anchor = row[0]

            same_row = (
                _vertical_overlap(item, row_anchor) >= overlap_threshold
                or abs(item["y_center"] - row_anchor["y_center"])
                <= max(item["height"], row_anchor["height"]) * 0.65
            )

            if same_row:
                row.append(item)
                placed = True
                break

        if not placed:
            rows.append([item])

    for row in rows:
        row.sort(key=lambda x: x["x_min"])

    rows.sort(key=lambda row: min(x["y_center"] for x in row))

    return rows


def rows_to_lines(rows):
    lines = []

    for row in rows:
        text = " ".join(item["text"] for item in row)

        confidence_values = [item["confidence"] for item in row]
        avg_confidence = sum(confidence_values) / len(confidence_values)

        lines.append({
            "text": text.strip(),
            "confidence": avg_confidence,
            "tokens": row,
        })

    return lines


def merge_same_line(ocr_result):
    items = normalize_ocr_items(ocr_result)
    rows = group_items_into_rows(items)
    return rows_to_lines(rows)