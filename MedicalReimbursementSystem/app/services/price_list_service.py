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
    def _to_decimal(value):
        if value is None or str(value).strip() == "":
            return None

        try:
            return Decimal(str(value).replace(",", "").strip())
        except InvalidOperation:
            return None

    @staticmethod
    def create_item(form_data):
        institution_id = form_data.get("institution_id", "").strip()
        service_name = form_data.get("service_name", "").strip()
        service_category = form_data.get("service_category", "").strip()

        cash_price = PriceListService._to_decimal(
            form_data.get("cash_price")
        )

        discount = PriceListService._to_decimal(
            form_data.get("discount")
        )

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
            service_category=service_category,
            cash_price=cash_price,
            discount=discount,
            approved_price=approved_price
        )

        return True, "Price list item created successfully."