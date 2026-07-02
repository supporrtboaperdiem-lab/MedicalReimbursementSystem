from app.extensions import db
from app.models.price_list import PriceListItem


class PriceListRepository:
    @staticmethod
    def get_by_batch(batch_id):
        return PriceListItem.query.filter_by(
            batch_id=batch_id
        ).order_by(
            PriceListItem.id.asc()
        ).all()

    @staticmethod
    def get_by_id(item_id):
        return PriceListItem.query.get(item_id)

    @staticmethod
    def get_by_batch_and_service(batch_id, service_name):
        return PriceListItem.query.filter_by(
            batch_id=batch_id,
            service_name=service_name
        ).first()

    @staticmethod
    def create(batch_id, institution_id, service_name, approved_price):
        item = PriceListItem(
            batch_id=batch_id,
            institution_id=institution_id,
            service_name=service_name,
            approved_price=approved_price
        )

        db.session.add(item)
        db.session.commit()

        return item

    @staticmethod
    def update(item, service_name, approved_price):
        item.service_name = service_name
        item.approved_price = approved_price

        db.session.commit()

        return item

    @staticmethod
    def delete(item):
        db.session.delete(item)
        db.session.commit()