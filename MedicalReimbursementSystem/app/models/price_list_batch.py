from app.extensions import db
from app.models.base import BaseModel


class PriceListBatch(BaseModel):
    __tablename__ = "price_list_batches"

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="PENDING"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    institution = db.relationship(
        "Institution",
        back_populates="price_list_batches"
    )

    items = db.relationship(
        "PriceListItem",
        back_populates="batch",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PriceListBatch {self.name} - {self.status}>"