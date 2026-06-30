from app.extensions import db
from app.models.base import BaseModel


class PriceListItem(BaseModel):
    __tablename__ = "price_list_items"

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

    service_category = db.Column(
        db.String(100),
        nullable=True
    )

    cash_price = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    discount = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    approved_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    effective_from = db.Column(
        db.Date,
        nullable=True
    )

    effective_to = db.Column(
        db.Date,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    institution = db.relationship(
        "Institution",
        back_populates="price_list_items"
    )

    def __repr__(self):
        return f"<PriceListItem {self.service_name} - {self.approved_price}>"