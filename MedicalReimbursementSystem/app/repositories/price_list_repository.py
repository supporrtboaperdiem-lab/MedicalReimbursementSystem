from app.extensions import db
from app.models.price_list import PriceListItem


class PriceListRepository:
    @staticmethod
    def get_all():
        return PriceListItem.query.order_by(
            PriceListItem.created_at.desc()
        ).all()

    @staticmethod
    def get_by_id(item_id):
        return PriceListItem.query.get(item_id)

    @staticmethod
    def get_by_institution_and_service(institution_id, service_name):
        return PriceListItem.query.filter_by(
            institution_id=institution_id,
            service_name=service_name
        ).first()

    @staticmethod
    def create(institution_id, service_name, approved_price):
        item = PriceListItem(
            institution_id=institution_id,
            service_name=service_name,
            approved_price=approved_price,
            approval_status="PENDING",
        )

        db.session.add(item)
        db.session.commit()

        return item

    @staticmethod
    def update(item, service_name, approved_price):
        item.service_name = service_name
        item.approved_price = approved_price
        item.approval_status = "PENDING"

        db.session.commit()
        return item

    @staticmethod
    def approve(item):
        item.approval_status = "APPROVED"
        db.session.commit()
        return item

    @staticmethod
    def reject(item):
        item.approval_status = "REJECTED"
        db.session.commit()
        return item

    @staticmethod
    def delete(item):
        db.session.delete(item)
        db.session.commit()