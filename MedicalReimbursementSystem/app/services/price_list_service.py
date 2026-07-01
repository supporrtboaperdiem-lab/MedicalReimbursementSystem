import os
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from app.models.institution import Institution
from app.repositories.price_list_batch_repository import PriceListBatchRepository
from app.repositories.price_list_repository import PriceListRepository
from app.services.ocr import extract_numeric_lines
from app.services.price_list_extraction_service import PriceListExtractionService


class PriceListService:
    @staticmethod
    def list_batches():
        return PriceListBatchRepository.get_all()

    @staticmethod
    def list_institutions():
        return Institution.query.order_by(Institution.name.asc()).all()

    @staticmethod
    def get_batch(batch_id):
        return PriceListBatchRepository.get_by_id(batch_id)

    @staticmethod
    def get_batch_items(batch_id):
        return PriceListRepository.get_by_batch(batch_id)

    @staticmethod
    def get_item(item_id):
        return PriceListRepository.get_by_id(item_id)

    @staticmethod
    def _to_decimal(value):
        try:
            return Decimal(str(value).replace(",", "").strip())
        except (InvalidOperation, AttributeError):
            return None

    @staticmethod
    def upload_price_list(form_data, file, upload_folder):
        institution_id = form_data.get("institution_id", "").strip()
        batch_name = form_data.get("batch_name", "").strip()

        if not institution_id:
            return False, "Institution is required.", None

        if not batch_name:
            return False, "Price list name is required.", None

        if not file or not file.filename:
            return False, "Price list file is required.", None

        original_name = secure_filename(file.filename)
        extension = Path(original_name).suffix.lower()

        if extension not in [".pdf", ".jpg", ".jpeg", ".png"]:
            return False, "Only PDF, JPG, JPEG, and PNG files are allowed.", None

        os.makedirs(upload_folder, exist_ok=True)

        stored_name = f"{uuid4().hex}_{original_name}"
        file_path = os.path.join(upload_folder, stored_name)

        file.save(file_path)

        batch = PriceListBatchRepository.create(
            institution_id=institution_id,
            name=batch_name
        )

        ocr_records = extract_numeric_lines(file_path, save_debug_pages=False)

        extracted_items, conflicts = PriceListExtractionService.extract_items(
            ocr_records
        )

        inserted = 0

        for item in extracted_items:
            existing = PriceListRepository.get_by_batch_and_service(
                batch_id=batch.id,
                service_name=item["service_name"]
            )

            if existing:
                continue

            PriceListRepository.create(
                batch_id=batch.id,
                institution_id=institution_id,
                service_name=item["service_name"],
                approved_price=item["approved_price"]
            )

            inserted += 1

        message = (
            f"Price list uploaded. {inserted} unique services extracted."
        )

        if conflicts:
            message += f" {len(conflicts)} conflicting duplicate services were skipped."

        return True, message, batch.id

    @staticmethod
    def update_item(item_id, form_data):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        if item.batch.status == "APPROVED":
            return False, "Approved price lists cannot be edited."

        service_name = form_data.get("service_name", "").strip()
        approved_price = PriceListService._to_decimal(
            form_data.get("approved_price")
        )

        if not service_name:
            return False, "Service name is required."

        if approved_price is None:
            return False, "Approved price is required and must be numeric."

        duplicate = PriceListRepository.get_by_batch_and_service(
            batch_id=item.batch_id,
            service_name=service_name
        )

        if duplicate and duplicate.id != item.id:
            return False, "This service already exists in this price list."

        PriceListRepository.update(
            item=item,
            service_name=service_name,
            approved_price=approved_price
        )

        return True, "Service price updated."

    @staticmethod
    def delete_item(item_id):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        if item.batch.status == "APPROVED":
            return False, "Approved price lists cannot be changed."

        batch_id = item.batch_id

        PriceListRepository.delete(item)

        return True, f"Service removed from price list.", batch_id

    @staticmethod
    def approve_batch(batch_id):
        batch = PriceListBatchRepository.get_by_id(batch_id)

        if not batch:
            return False, "Price list batch not found."

        items = PriceListRepository.get_by_batch(batch_id)

        if not items:
            return False, "Cannot approve an empty price list."

        PriceListBatchRepository.approve(batch)

        return True, "Price list approved and activated."

    @staticmethod
    def reject_batch(batch_id):
        batch = PriceListBatchRepository.get_by_id(batch_id)

        if not batch:
            return False, "Price list batch not found."

        PriceListBatchRepository.reject(batch)

        return True, "Price list rejected."