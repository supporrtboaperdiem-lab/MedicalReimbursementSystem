from app.extensions import db
from app.models.base import BaseModel


class PriceListItem(BaseModel):
    __tablename__ = "price_list_items"

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("price_list_batches.id"),
        nullable=False,
        index=True
    )

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id"),
        nullable=False,
        index=True
    )

    service_name = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    approved_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    batch = db.relationship(
        "PriceListBatch",
        back_populates="items"
    )

    institution = db.relationship(
        "Institution",
        back_populates="price_list_items"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "batch_id",
            "service_name",
            name="uq_batch_service_price"
        ),
    )

    def __repr__(self):
        return f"<PriceListItem {self.service_name} - {self.approved_price}>"