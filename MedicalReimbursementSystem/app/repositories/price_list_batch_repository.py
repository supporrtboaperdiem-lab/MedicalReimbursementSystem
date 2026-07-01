from app.extensions import db
from app.models.price_list_batch import PriceListBatch


class PriceListBatchRepository:
    @staticmethod
    def get_all():
        return PriceListBatch.query.order_by(
            PriceListBatch.created_at.desc()
        ).all()

    @staticmethod
    def get_by_id(batch_id):
        return PriceListBatch.query.get(batch_id)

    @staticmethod
    def create(institution_id, name):
        batch = PriceListBatch(
            institution_id=institution_id,
            name=name,
            status="PENDING",
            is_active=False
        )

        db.session.add(batch)
        db.session.commit()

        return batch

    @staticmethod
    def approve(batch):
        batch.status = "APPROVED"
        batch.is_active = True
        db.session.commit()
        return batch

    @staticmethod
    def reject(batch):
        batch.status = "REJECTED"
        batch.is_active = False
        db.session.commit()
        return batch