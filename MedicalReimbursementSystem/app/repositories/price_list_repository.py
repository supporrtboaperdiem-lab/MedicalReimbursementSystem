from app.extensions import db
from app.models.price_list import PriceListItem


class PriceListRepository:
    @staticmethod
    def get_all():
        return PriceListItem.query.order_by(
            PriceListItem.created_at.desc()
        ).all()

    @staticmethod
    def get_by_institution_and_service(institution_id, service_name):
        return PriceListItem.query.filter_by(
            institution_id=institution_id,
            service_name=service_name
        ).first()

    @staticmethod
    def create(
        institution_id,
        service_name,
        approved_price,
        service_category=None,
        cash_price=None,
        discount=None
    ):
        item = PriceListItem(
            institution_id=institution_id,
            service_name=service_name,
            service_category=service_category,
            cash_price=cash_price,
            discount=discount,
            approved_price=approved_price,
        )

        db.session.add(item)
        db.session.commit()

        return item