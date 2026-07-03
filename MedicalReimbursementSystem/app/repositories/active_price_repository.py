from app.models.price_list import PriceListItem
from app.models.price_list_batch import PriceListBatch


class ActivePriceRepository:
    @staticmethod
    def get_active_price(institution_id, service_name):
        active_batch = PriceListBatch.query.filter_by(
            institution_id=institution_id,
            status="APPROVED",
            is_active=True
        ).first()

        if not active_batch:
            return None

        return PriceListItem.query.filter_by(
            batch_id=active_batch.id,
            service_name=service_name
        ).first()

    @staticmethod
    def get_active_batch(institution_id):
        return PriceListBatch.query.filter_by(
            institution_id=institution_id,
            status="APPROVED",
            is_active=True
        ).first()