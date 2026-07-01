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

    approved_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
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

    __table_args__ = (
        db.UniqueConstraint(
            "institution_id",
            "service_name",
            name="uq_institution_service_price"
        ),
    )

    def __repr__(self):
        return f"<PriceListItem {self.service_name} - {self.approved_price}>"