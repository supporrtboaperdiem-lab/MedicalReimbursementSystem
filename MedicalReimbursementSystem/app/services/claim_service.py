import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from app.models.institution import Institution
from app.repositories.active_price_repository import ActivePriceRepository
from app.repositories.claim_repository import ClaimRepository
from app.services.claim_extraction_service import ClaimExtractionService
from app.services.ocr import extract_numeric_lines


class ClaimService:
    @staticmethod
    def list_claims():
        return ClaimRepository.get_all()

    @staticmethod
    def list_institutions():
        return Institution.query.order_by(Institution.name.asc()).all()

    @staticmethod
    def get_claim(claim_id):
        return ClaimRepository.get_by_id(claim_id)

    @staticmethod
    def submit_claim(form_data, file, upload_folder):
        institution_id = form_data.get("institution_id", "").strip()
        patient_name = form_data.get("patient_name", "").strip()

        if not institution_id:
            return False, "Institution is required.", None

        if not patient_name:
            return False, "Patient name is required.", None

        if not file or not file.filename:
            return False, "Receipt file is required.", None

        active_batch = ActivePriceRepository.get_active_batch(institution_id)

        if not active_batch:
            return False, "This institution has no active approved price list.", None

        original_name = secure_filename(file.filename)
        extension = Path(original_name).suffix.lower()

        if extension not in [".pdf", ".jpg", ".jpeg", ".png"]:
            return False, "Only PDF, JPG, JPEG, and PNG files are allowed.", None

        os.makedirs(upload_folder, exist_ok=True)

        stored_name = f"{uuid4().hex}_{original_name}"
        file_path = os.path.join(upload_folder, stored_name)

        file.save(file_path)

        claim = ClaimRepository.create_claim(
            institution_id=institution_id,
            patient_name=patient_name,
            receipt_file_path=file_path
        )

        ocr_records = extract_numeric_lines(
            file_path,
            save_debug_pages=False
        )

        extracted_items = ClaimExtractionService.extract_items(ocr_records)

        inserted = 0

        for item in extracted_items:
            active_price = ActivePriceRepository.get_active_price(
                institution_id=institution_id,
                service_name=item["service_name"]
            )

            if active_price:
                approved_price = active_price.approved_price
                difference = item["receipt_price"] - approved_price

                if difference == Decimal("0"):
                    status = "MATCHED"
                elif difference > 0:
                    status = "OVER_PRICE"
                else:
                    status = "UNDER_PRICE"
            else:
                approved_price = None
                difference = None
                status = "UNKNOWN_SERVICE"

            ClaimRepository.create_item(
                claim_id=claim.id,
                service_name=item["service_name"],
                receipt_price=item["receipt_price"],
                approved_price=approved_price,
                difference=difference,
                validation_status=status
            )

            inserted += 1

        return True, f"Claim submitted. {inserted} receipt items extracted.", claim.id

    @staticmethod
    def approve_claim(claim_id):
        claim = ClaimRepository.get_by_id(claim_id)

        if not claim:
            return False, "Claim not found."

        ClaimRepository.approve_claim(claim)

        return True, "Claim approved."

    @staticmethod
    def reject_claim(claim_id):
        claim = ClaimRepository.get_by_id(claim_id)

        if not claim:
            return False, "Claim not found."

        ClaimRepository.reject_claim(claim)

        return True, "Claim rejected."