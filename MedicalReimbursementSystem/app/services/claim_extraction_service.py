import re
from decimal import Decimal, InvalidOperation

NUMBER_PATTERN = r'\(?-?\d[\d,]*(?:\.\d+)?\)?'


class ClaimExtractionService:
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
        service = re.sub(r"^[A-Z]{2,5}\d+[A-Z0-9.]*\s*", "", service).strip()

        return service

    @staticmethod
    def extract_items(ocr_records):
        items = []

        for record in ocr_records:
            text = record.get("text")

            if not text:
                continue

            numbers = re.findall(NUMBER_PATTERN, text)

            if not numbers:
                continue

            receipt_price = ClaimExtractionService.normalize_number(numbers[-1])

            if receipt_price is None:
                continue

            service_name = ClaimExtractionService.clean_service_name(text, numbers)

            if not service_name:
                continue

            items.append({
                "service_name": service_name,
                "receipt_price": receipt_price,
                "raw_text": text,
                "page": record.get("page")
            })

        return items