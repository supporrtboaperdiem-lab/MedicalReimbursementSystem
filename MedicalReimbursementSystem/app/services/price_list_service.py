from decimal import Decimal, InvalidOperation

from app.models.institution import Institution
from app.repositories.price_list_repository import PriceListRepository


class PriceListService:
    @staticmethod
    def list_items():
        return PriceListRepository.get_all()

    @staticmethod
    def list_institutions():
        return Institution.query.order_by(Institution.name.asc()).all()

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
    def create_item(form_data):
        institution_id = form_data.get("institution_id", "").strip()
        service_name = form_data.get("service_name", "").strip()
        approved_price = PriceListService._to_decimal(
            form_data.get("approved_price")
        )

        if not institution_id:
            return False, "Institution is required."

        if not service_name:
            return False, "Service name is required."

        if approved_price is None:
            return False, "Approved price is required and must be numeric."

        existing = PriceListRepository.get_by_institution_and_service(
            institution_id=institution_id,
            service_name=service_name
        )

        if existing:
            return False, "This service already exists for this institution."

        PriceListRepository.create(
            institution_id=institution_id,
            service_name=service_name,
            approved_price=approved_price
        )

        return True, "Price list item created successfully."

    @staticmethod
    def update_item(item_id, form_data):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        service_name = form_data.get("service_name", "").strip()
        approved_price = PriceListService._to_decimal(
            form_data.get("approved_price")
        )

        if not service_name:
            return False, "Service name is required."

        if approved_price is None:
            return False, "Approved price is required and must be numeric."

        duplicate = PriceListRepository.get_by_institution_and_service(
            institution_id=item.institution_id,
            service_name=service_name
        )

        if duplicate and duplicate.id != item.id:
            return False, "Another service with this name already exists for this institution."

        PriceListRepository.update(
            item=item,
            service_name=service_name,
            approved_price=approved_price
        )

        return True, "Price list item updated successfully."

    @staticmethod
    def delete_item(item_id):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        PriceListRepository.delete(item)

        return True, "Price list item deleted successfully."
    
    @staticmethod
    def approve_item(item_id):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        PriceListRepository.approve(item)
        return True, "Price list item approved successfully."

    @staticmethod
    def reject_item(item_id):
        item = PriceListRepository.get_by_id(item_id)

        if not item:
            return False, "Price list item not found."

        PriceListRepository.reject(item)
        return True, "Price list item rejected successfully."