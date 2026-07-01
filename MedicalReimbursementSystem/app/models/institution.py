from app.extensions import db
from app.models.base import BaseModel


class Institution(BaseModel):
    __tablename__ = "institutions"

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
        index=True
    )

    institution_type = db.Column(
        db.String(50),
        nullable=False
    )

    address = db.Column(
        db.String(255),
        nullable=True
    )

    phone = db.Column(
        db.String(50),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    expenses = db.relationship(
        "Expense",
        back_populates="institution",
        lazy=True
    )

    documents = db.relationship(
        "Document",
        back_populates="institution",
        lazy=True
    )

    price_list_items = db.relationship(
        "PriceListItem",
        back_populates="institution",
        lazy=True
    )
    price_list_batches = db.relationship(
        "PriceListBatch",
        back_populates="institution",
        lazy=True
    )

    def __repr__(self):
        return f"<Institution {self.name}>"