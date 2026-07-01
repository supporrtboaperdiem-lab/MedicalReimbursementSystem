import re
from decimal import Decimal, InvalidOperation

NUMBER_PATTERN = r'\(?-?\d[\d,]*(?:\.\d+)?\)?'


class PriceListExtractionService:
    @staticmethod
    def normalize_number(value):
        try:
            cleaned = str(value).replace(",", "").replace("(", "-").replace(")", "")
            return Decimal(cleaned)
        except InvalidOperation:
            return None

    @staticmethod
    def clean_service_name(text, numbers):
        service = text

        for n in numbers:
            service = service.replace(n, "")

        service = re.sub(r"\s+", " ", service).strip()

        # Remove common service codes at beginning, e.g. DKL171, DKOPV223
        service = re.sub(r"^[A-Z]{2,5}\d+[A-Z0-9.]*\s*", "", service).strip()

        return service

    @staticmethod
    def extract_items(ocr_records):
        """
        Convert OCR JSON rows into unique service -> approved_price rows.

        Rule:
        - one service appears once
        - approved price is the last numeric value in the line
        - exact duplicates are ignored
        - same service with different prices is marked as conflict and skipped for now
        """

        unique = {}
        conflicts = []

        for record in ocr_records:
            text = record.get("text")

            if not text:
                continue

            numbers = re.findall(NUMBER_PATTERN, text)

            if not numbers:
                continue

            approved_price = PriceListExtractionService.normalize_number(numbers[-1])

            if approved_price is None:
                continue

            service_name = PriceListExtractionService.clean_service_name(text, numbers)

            if not service_name:
                continue

            key = service_name.lower()

            if key not in unique:
                unique[key] = {
                    "service_name": service_name,
                    "approved_price": approved_price,
                    "raw_text": text,
                    "page": record.get("page"),
                }
                continue

            existing = unique[key]

            if existing["approved_price"] != approved_price:
                conflicts.append({
                    "service_name": service_name,
                    "existing_price": existing["approved_price"],
                    "new_price": approved_price,
                    "raw_text": text,
                    "page": record.get("page"),
                })

        return list(unique.values()), conflicts